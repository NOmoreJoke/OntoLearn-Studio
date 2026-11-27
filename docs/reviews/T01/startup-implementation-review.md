# T01 business3/startup 实施阶段验收

本阶段已完成真实引擎启动、严格协议3内部选择、启动失败来源认证及跨层安全展示的实现；默认生产入口仍为协议2。固定17产品/8测试通过全仓检查、独立代码审查与未签名包的无窗口验证。此结论仅限本阶段，不等于项目与事务父功能、指定双审、真实 Electron IPC/UI、远端 CI 或发布完成。

## 授权及固定输入

- 原Goal和工作树保持：`feature/weekly-t01-project-transactions`，本阶段起点 `79d6bc4998ef49f8401636166b7e9fa7193c6b21`，批准集成基线 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 最终五字段封套授权 SHA256 `3054a5ca2393ce6178e537c150f31b8fc0c63f3d28527a61b53cadeebfd6f334`；采用实施计划 `e9999d37a034fc365b8c5a345c3c135220e13c78b4f4907a763d81351d846b07`。
- 旧 `task-runtime.test.ts` 仅依精确单文件临时窗授权 `6764ab1fd75458dce7cbe9c7fdd3edea9825b91ae6997fceac8f42801949eb14`，effective JSON `a29d2f34ee2c5ed4d78b6c77c0303b39939450eb9eeaf8688452a749f2367fe5`。T01本轮唯一临时writer，原I05只读；永久责任与窗口关闭仍由总控登记。
- [最终源码清单](evidence/startup-final-source.json) 4500B，SHA256 `6ef21895a7e2b370f87896bc4f79a04425de852751cef16272a1f124d798c5b4`；[完整输入 ZIP](evidence/startup-final-source.zip) 175431B，SHA256 `d3927873679cb89bf28031023f89081301df70c3c63a655afc6d588b5ed6e86a`。26唯一成员含25条实际源码/测试和原样清单，已逐成员回读；独立审查另行核对一致。
- AGENTS保持未暂存，SHA256 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`。未修改I06余四、worker、protocol/resources、project/format3、打包/依赖/锁/CI或其他旧通用测试。

## 实际实现

canonical新增独立 `startupFailure` 五字段封套及四种有限错误；格式不支持只出现在该启动通道。严格校验真实UTF-8 payload预算1024字节、同源registry hash及完整结构。普通2/3协议、旧defs、sourceTable和默认2保持既有含义。registry最终实际bytes SHA256 `271800b8f3ca3946b71d9ca07da24c251a0842f66bf6f806b96ac1b1767ff9fa`，状态为 `explicit-internal-opt-in-default2`。

Python以显式有限argv启用内部business3。真实Store3、JobStore3和reconcile全部成功后才允许hello选3；正式请求/响应/通知同版，worker内部协议不变。Store/Job构造逐资源独立清理并保留第一cause，父子只在成功后转移所有权。实际高格式版本使用typed异常；资源未可信加载时不伪造同源诊断。初始化失败最多一条完整诊断、LF/flush和非零退出，ready后不回到启动通道。reader状态区分stop请求、线程实际结束和保守settled，不关闭用户stdin、不跨线程操作reader、不无限join。

desktop使用实际ES `#private`、原Session/attempt/generation和原操作promise登记来源；真实listener的每份交付clone分别签发，公开shape/普通clone/新Error/错promise/跨实例都不取得权限。同步首错终止清reader并阻止同chunk后续帧；TaskService/main保留原请求或health promise，嵌套guard只能转交私有登记的原结果及原promise。展示仅有限DTO和固定文案，不暴露原始路径或数据库实际版本。共享preload/renderer原过滤链仅做静态接线核对，没有真实IPC/UI运行证据。

## 独立意见与失败历史

[独立实现审查](startup-implementation-independent-review.md) 保留各初组身份、首探针失败、修后定点和最终统一输入。当前无未解决实质代码阻断：

| 项目 | 实际处置及证据 |
| --- | --- |
| P2-S1 错Session通知未终止 | business3同步终态；独立同chunk错通知/正通知/health探针：INVALID_REQUEST、0通知、Session清除。 |
| root P2 嵌套guard吞掉合法[3] | 修前真实Coordinator反例实际失败；修后原结果+原promise私有绑定保留VERSION_INCOMPATIBLE/[3]，clone/替换promise负例拒绝，独立定点通过。 |
| reader settled证据过强风险 | 最小内部状态区分请求与实际停止，真实daemon受控阻塞机制独立通过；未称真实stdin已立即释放。 |
| 旧测试反射私有Map | 不开放生产私有字段；在唯一临时窗应用r2 wire观测：完整request/response匹配与双方向无半帧；原8个测试名/期限/真实进程/幂等断言保持。它证明完整wire响应，不直接证明私有Map本体。 |
| 转义预算pair证据缺口 | 原13raw保留，追加相同decoded完整值、140个实际转义的1024/1025字节完整原件；真实reader与Python独立核，接受/拒绝正确。 |

首轮全仓运行实际3旧反射测试失败（1024通过，后续build/Python未到达），不是通过。第二轮仅迁移说明的Prettier失败，单独格式化说明后再完整运行。受控Job测试最初因未建立live订阅零事件失败，后以明确workMs500夹具确保真实queued/running订阅后继续全部原断言。初次缺helper、Python夹具错误、测试lint以及独立探针的参数/对象原型错误均保留原工具对象和日志；不改写成产品缺陷或首稿通过。修前两源码输入另有原样ZIP，不以修后文件重建修前证据。

## 实际验证终态

| 命令 / 范围 | 终态与原件 |
| --- | --- |
| `npm run check` | session20694/chunk1a3ca0 exit0；1030TS，2706Python，44原有不适用skip；lint/Prettier/type/build/ruff全过。完整日志8029B SHA256 `f33b8aba4a42afa4e0d9eb12d354bcdeebfdd0c4f1d918d9cb24d9d4c460cf24`。 |
| `npm run verify:sources` | 原材料12输入核验exit0；日志111B SHA256 `1439dca3a0fd2dbc3702b336e9accceedc93893d0d65264c69da1aa175c45536`；此后未改其输入，不重复运行。 |
| `npm run package:dir` | session95246/chunk80910e exit0；实际PyInstaller+mac-arm64目录包；配置identity=null，日志明确跳过签名。日志14324B SHA256 `b1fac97983ca7f34a5694c73e5833bf94cfc6d469fb71471a4dd3d9c779ca184`。 |
| 新包引擎真实stdio | session63701/chunk2a9c3b exit0；5真实session：默认2/显式3健康、未来格式4安全诊断退出1且原库版本不动、包内Coordinator+worker原子Job、重开同operation幂等；claim1/revision增1。完整原stdin/stdout/stderr含bytes/hash/base64，JSON58234B SHA256 `2dbb6ccd116c769852853b2424aa843e5497c4abfe539fac70ef994643265e5f`。 |
| 新包静态资源/编译绑定 | chunkfdfdb9 exit0；asar内main与实际构建main逐字节一致，AST只解析数据完整值与canonical registry相等；8JSON在desktop/engine两处均同源，helper/lock及构建/包内engine一致。结果1950B SHA256 `0e275620f8cd69a3cdf0cb084f120c9f578278003c2a070f8280b0a436ff2124`。 |

新main为388655B/SHA256 `46e6b7908b29dc71b20f6c0e25081285ce258f3ba0c41983202413092a06b9f3`。包内引擎可执行文件SHA256 `e815d4aa7ee6fce29aba4f18531bc07bac6392fcf45895c9943cdeaed923df25`；其自身可执行字节未因fixtures数据变化而改变，但两处fixtures实际新hash和完整资源manifest均已独立绑定，不能只凭exe hash代替资源验证。更早成功包属于旧TaskService候选，保留原件，不算本次新main证明。

以上均未启动桌面artifact、Electron handler、native、e2e、HMR或审查应用，不把下载/构建Electron当窗口启动。真实Electron IPC/renderer交互仍待隔离环境；指定ZCode GLM-5.3最高、MiniMax Code M3.1-Flash/xhigh双审及远端PR/CI/正常develop合并尚未完成，双审前不push。原Goal保持active，接续完整项目/事务、来源/学习/恢复与跨功能正式验收，不以本阶段代替父功能完成。

## 封存和交接

[原始证据包](evidence/startup-raw-evidence.tar.gz) 672930B，SHA256 `5fff9da5a2c9eccf8cd13ab8099768e7f888d85bfb61409f9c899e966ea89039`；[逐原件索引](evidence/startup-raw-evidence.json) 185341B，SHA256 `ff446b032c42c916aff541694b7aebbaec8ffd9e5aa424848f2ce7db40a69ce2`。61成员全部解包回读相同，包含四会话301对完整原工具call/output、全部本阶段临时日志（含失败/被替代版本）、新旧包完整原bytes记录/脚本及嵌套guard修前两源码ZIP。每行有原session路径、捕获prefix长度/hash、实际行号/offset/长度/hash；不从summary重建输出。入站消息无本地call和归档当时尚未完成的capture调用不冒作工具对；归档之后仅文档检查/Git交接另据正式执行记录，不假称已收入该固定包。

最终独立报告32421B，SHA256 `1afdbb2f8e4d6c4efba09fd796cf16d1aced4605ba1d71e7d66ae45046e7a5a7`，作者已停写。总控固定读回22721B/SHA256 `0e5efe360118e50455d9d22fc49a7a3a539b7900b2ea963b9f99b42549621b6f` 的原前缀与新增尾段已实际读完并核hash：根仅静态关闭P2-CHAIN/转义pair，仍待最终Git/包/raw交接，不自行替根登记阶段或临时窗口已关闭。准备本地恢复提交，固定25条source/test字节不变；AGENTS继续不stage。
