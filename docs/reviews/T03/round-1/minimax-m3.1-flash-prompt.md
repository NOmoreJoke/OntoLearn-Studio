# MiniMax M3.1-Flash：T03-S1 完整独立冻结审查提示

指定应用/模型：**MiniMax M3.1-Flash**；思考等级：**xhigh**；本任务实际权限必须读回 **permissionMode=bypassPermissions**。不降级、不换模型。真实task ID=null、lease=NOT_GRANTED，尚未开始。经总控/T06实际派发后，先把真实task ID/model/effort/mode/lease读回写入报告；不能只凭用户级默认配置或界面名声明匹配。

你是独立对抗审查者。本文件是待lease授予后使用的完整冻结提示，当前仅准备；不是创建任务/启动模型的授权。没有总控对精确base/head的外审lease时停止于材料核验并报告NOT_GRANTED，不启动外部调用。T06是当前唯一后台入口恢复owner，不抢建任务、不重建聊天/Goal。

任务：从批准base `5f910b52c69d86a1076b2032e5d3c63e715947f3` 全量审查完整candidate `30319412daf8ae4745987babf7bbed93c53b6b42` 的T03-S1私有映射服务、页面状态、三依赖/构建/受限probe以及全部新增测试、验收、证据。产品/原包输入为 `0ad7e0a75cc4583918b057885631934c0a9bd859`，不以0ad替代303最终测试验收。准备前process HEAD `0b3ccdeb0732610b1483993c0cb70ab888b19ce3`，后续本round-1只能过程docs；两任务受审身份必须完全相同。

工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping`，分支 `feature/weekly-t03-mapping`。先普通Git核HEAD/branch/status、base和candidate均可解析；无checkout/reset/clean。按固定candidate读取全部75路径，参考当前最新操作AGENTS（15852B/SHA `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`，保护M未stage），不能以旧base指南覆盖现行无桌面/权限规定。current/status只有后续过程追加，原始审查数据从303读取。若实际代码/测试/依赖/验收或base变化，停止沿用旧候选通过，报告需新candidate/联验与双方新审；不能自行改冻结物。

必读：本目录 `scope-and-evidence.md`、`scope-and-identities.json`、`evidence-index.json`、`preparation-manifest.json`；303下 `docs/iterations/T03/T03-S1-scope.md`、`acceptance.md`、`integration-request.md`、`parser-dependency-candidate.json`；PRD `docs/prd/PRD-本体学习与落地Agent工作台.md` 的FR-300–304、附录D/G.1 M-01–06、11–12相关全文（保父项未验，不能以子阶段改写需求）。查看base→303完整diff与必要未改依赖源码/调用方，不能只审最后提交或依赖摘要。外部总控目录 `/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release/` 的T03启动/候选核验/权限材料只作真实既有背景；不读其他线变化实现/状态、凭据、应用任务数据库。

完整审查关注：

1. CSV/XLSX真实解析、sheet/编码/公式缓存含空缓存与缺缓存/稀疏值、宏/危险XML/资源边界。外部formula/hyperlink仅读保存缓存或显示文本，不执行或联网，含URL本身不必拒绝。读两OOXML固定样例socket.socket/create_connection/getaddrinfo零调用断言及CSV bytes/columns/cell/rows四边界，区分固定路径证据与所有OS/所有潜在构造；不把CSV测试冒称所有XLSX预算逐项实测。
2. 完整四事实、001字符串、单/复合身份和跨表引用、显式转换与准确行字段错误、重复执行幂等、删除仅撤本映射、人工漂移/墓碑/多来源冲突整批暂停、source/definition/version/旧预览拒绝。不得把expected灌入Store当实际结果。
3. 真实Store准备计划/来源/owner/managed/row元数据/完整历史；取消/失败/真实os._exit在提交前、中回滚及提交后标记对账，完整集合断言与6字段元数据，不能把投递失败当零提交。现有真实Store内部证据不证明I04正式业务Job已接线。
4. 私有三步页面的project/revision/source/selection/sheet/encoding/generation/draft绑定、迟到/取消不复活、显式确认/冲突阻断、缺回调禁用、SSR恶意文本转义。页面未挂App、无公共bridge/能力注册；unit/types/build不证明浏览器交互。
5. 有效移交的四文件pyproject/uv.lock/build-engine/entrypoint，三精确依赖openpyxl3.1.5/et-xmlfile2.0.0/defusedxml0.7.1及完整license/hash，原非engine17包记录保持、锁与包一致、固定probe不能提供任意文件/脚本/参数入口。查正常/-O/额外参数/固定错误，旧CLI保持。不得按最新版猜依赖合规或修改公共14文件/CI/resources等责任。
6. 全部验收、原件和身份链。最新完整check原件 `docs/reviews/T03/check-registered-scope.txt` 应全文读至最终exit：638TS/1110Python/零skip、mapping58，source21包含新增3实例。读 `project-candidate-validation.json`、`registered-scope-delta.json`、完整必要raw以及首失败/修复记录，历史overlay/4skip、1107或旧55项不替代最新303。当前18source已按current=303=登记SHA核对；你仍需以完整scope独立分析，不能将此当代码审查通过。
7. 原 `package-dir-first.txt`、`product-package-verification.json`、`product-package-identity.json`、source/package完整stdout/stderr、verifier和existing storage原件。原包输入0ad→303产品不变，继承的是固定实物和既有11组CLI证据，没有为新增OOXML源码测试重包/重跑，不能倒贴成新包内实例。原包670项（656regular+14symlink），regular347512381B；engine SHA `5f40a5654350eec58db51000055e7157b452f6c9ca3294a47b646c7831aea482`，asar SHA `bc731a46b957aa38ed1d2abc9782fba4e554190323510bb439926fc4e5679ad8`，lock SHA `9f5b6d2b93d994a3e4f8a46ce5cccae99d4e024ea7531ab62dd8e85d6aa1152e`。manifest实际文件含LF SHA `98e2d8478d366d2463681d9232ea56353039a951043f90a911743fd230afc860`，canonical无LF SHA `9271f6c7b172f6591ec31434cced70ed68b0145c14bc1dc8ed8d08a1f1e28b5c`，不可混用；已知main compiled仅dev CSP随机nonce不同，不称全部compiled五件逐字相同。额外参数拒绝的旧包证据由冻结verifier执行路径/成功receipt支持，缺独立三件raw边界保留。macOS27 arm64 unsigned目录CLI不等于macOS15/Windows11、签名安装、GUI或生产。
8. `root-artifact-recovery.json`及`ignored-artifact-archive.json`的E1保全闭环；canonical350826496B归档SHA `7dfe86826a2b35ceefa5d50b25fb778c6a2c694c18a75d26ac75a4e62cf63b3b`，路径 `/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release/.private/T03-S1-303-artifact-recovery/application-and-original-manifest.tar`，index SHA `096e91716d794f6bdb8458f76475b8bd67d939822939f353a67b8b71dc74eef9`。本次只准读现有小原件/Git/hash，不自行复制/解码大包或执行；确需更强操作报告精确缺口交root单独授权。旧/root/t03_service_review内审不是本轮指定模型审查，既有内审判定不得替代你独立结论。

操作边界：只读代码/测试/配置/依赖/现成验收与原件，只有指定自己的report可以写；无stage/commit/push/PR/merge/切分支、无实现修复/新fixture/重测/重包/安装/网络/secret/新付费。当前不运行产品、引擎、prepared helper、test suite、GUI/Electron/e2e/native/HMR或外审应用；可用普通Git/文件/stdlib静态解析/hash，在内存分析，不写其他文件。完全访问/yolo/bypass只是模式，不扩授权。任何必需新执行或资源冲突先记具体待验交root，不静默模拟通过。另一个本轮模型报告/意见即使已存在也禁止读取/转发，两个独立新同版任务不能互泄；不读取另一模型当前报告，不以互相引用形成通过。

交付一个完整真实报告，不创建其他文件：记录实际task ID、模型精确名、思考等级、任务实际权限模式读回及lease依据；固定base/candidate/product/process/worktree/branch与读取范围；所有finding按优先级列准确文件/行、具体触发/反例、影响、证据与建议验证；区分代码问题、证据缺口和子范围外父验收，不把文件数/JSON摘要当全文阅读。若无finding也列验证依据与范围；旧问题须独立核验并逐条说明，所有未核事实明确未知。实际执行写命令/退出/原件，未执行不冒称；中断/失败/额度/路径问题保留，禁止删首错或用空报告假Pass。最后明确Pass/Fail/Blocked、仍开门及原因，报告完整终态后由root全文读回/逐条处置。

所有父门保持：正式文件/sheet选择、公共错误/分页/contracts/bridge/App、正式Store/Job/worker/producer/selected及恢复、T02/T08/T10、目标两OS/真人、SQLite损坏HOLD/wholeH、完整T03 FR-300–304/B1/父57P0。双方全新同版指定任务真实终态通过+意见关闭后才可考虑push/PR；CI/正常develop合并/远端核验保留，报告存在或协议进程/界面模型名不等于通过。

你的唯一可写report：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping/docs/reviews/T03/round-1/minimax-m3.1-flash-report.md`。禁止读另一模型本轮report `zcode-glm-5.3-report.md`；当前未创建任一report，不预填任何结论或终态。
