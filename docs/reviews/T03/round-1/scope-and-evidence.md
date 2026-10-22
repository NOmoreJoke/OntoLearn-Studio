# T03-S1 round-1 冻结审查准备

状态：PROMPTS_PREPARED_PENDING_CONTROLLER_LEASE。只有提示准备，ZCode/MiniMax 实际 task ID 均为 null，外审 lease=NOT_GRANTED，未启动任何外部模型。T06 是当前唯一后台入口恢复 owner；原 T03 仅交付本地材料，不操作 GUI、后台模型服务或任务数据库。

## 冻结身份

- base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 完整受审 candidate：`30319412daf8ae4745987babf7bbed93c53b6b42`，审查 base→candidate 全部75路径，包含最终新增测试和验收，不仅最后提交diff。
- 产品实现及原目录包输入：`0ad7e0a75cc4583918b057885631934c0a9bd859`。0ad→303只变测试/验收和证据，不能把0ad旧审查当303指定双审。
- 提示准备前 process HEAD：`0b3ccdeb0732610b1483993c0cb70ab888b19ce3`。303之后6路径均过程docs；当前status/current-candidate有过程追加，受审版本仍从303 Git读取。
- worktree：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping`；branch：`feature/weekly-t03-mapping`。保护AGENTS未暂存，15852B/SHA256 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`。

`scope-and-identities.json`列完整75路径candidate/current字节身份、4项修改文件base身份、18项current=303=登记SHA，以及完整6路径过程差异。`evidence-index.json`列60项既有合同/验收/原件及后续保全回执，既有check与包结果不代表本次重跑。`preparation-manifest.json`只列新准备payload，自身排除；actual过程commit由提交后外报，不能预填未来自身hash。

## 完整S1范围与验收

范围是私有CSV/XLSX解析、确定性映射/转换/引用和准备计划、来源所有权与重跑恢复、受控三步私有页面/状态、有效移交四文件中的三精确依赖/锁/构建收集与受限固定probe，以及全部专属测试/样例/验收和原件。不得只审最后3项测试，亦不得扩为其他T03 profile/native/I05或其他树。

完整验收包括：固定样本完整四事实与001字符串；同源重复幂等；源删除仅撤本映射、不删人工/其他来源；手工编辑/墓碑/多来源冲突整批暂停；空/重复主键、转换失败的具体行字段；旧预览/源/定义/版本拒绝；单/复合身份和跨表引用稳定；sheet选择、公式缓存/空缓存、缺缓存拒绝、稀疏值、宏/危险XML/非法编码和资源边界。外部公式与hyperlink只取已存缓存/显示文本，不能把含URL本身判为必拒绝。两个OOXML样例的三个socket入口零调用证据只覆盖该固定测试路径。CSV四类超限与XLSX所有声明资源边界分别评估，不把前者当后者全部实测。

Store准备计划需读完整RDF/来源/元数据/历史断言，覆盖取消、失败、真实os._exit在提交前/中回滚和提交后标记对账；不能把投递失败当零提交。私有页面需读项目/revision/source/selection/sheet/encoding/generation/draft绑定、迟到与取消失效、显式确认、冲突阻断、缺业务回调禁用、恶意文本SSR转义。该CLI/unit/state证据不证明真实浏览器交互或正式I04业务接线。

## 既有证据与边界

最新完整check原件 `docs/reviews/T03/check-registered-scope.txt`：既有exit0、638TS、1110Python、零skip、mapping58。`project-candidate-validation.json`登记18身份。应全文读完整check/raw、各首失败及修复链，不能仅引用JSON摘要；本次没有重测。

原 `package-dir-first.txt` 和 `product-package-verification.json`对应0ad相同产品输入，真实App内11组固定CLI与源码输出一致。新增OOXML两样例和CSV四边界属于303源码测试，原包没有新增这几组执行。包是macOS27 arm64 unsigned开发目录CLI，不是Windows11/macOS15、干净设备、签名安装、GUI或生产验收。

原包670项=656普通文件+14symlink，347512381B；引擎SHA `5f40a5654350eec58db51000055e7157b452f6c9ca3294a47b646c7831aea482`；asar SHA `bc731a46b957aa38ed1d2abc9782fba4e554190323510bb439926fc4e5679ad8`；锁SHA `9f5b6d2b93d994a3e4f8a46ce5cccae99d4e024ea7531ab62dd8e85d6aa1152e`。完整manifest实际文件（含末LF）SHA `98e2d8478d366d2463681d9232ea56353039a951043f90a911743fd230afc860`，规范内容（无LF）SHA `9271f6c7b172f6591ec31434cced70ed68b0145c14bc1dc8ed8d08a1f1e28b5c`。已知main compiled asset只差批准构建的development CSP随机nonce，不能称5个compiled asset全部逐字同。

原件保全E1由根独立恢复审计关闭，`root-artifact-recovery.json`记录canonical归档 `/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release/.private/T03-S1-303-artifact-recovery/application-and-original-manifest.tar`，350826496B/SHA `7dfe86826a2b35ceefa5d50b25fb778c6a2c694c18a75d26ac75a4e62cf63b3b`。index SHA `096e91716d794f6bdb8458f76475b8bd67d939822939f353a67b8b71dc74eef9`。本准备仅读小回执，没有读包、解码、复制或执行；后续审查若需要未授操作，应记具体缺口并由root另派，不自行解冻/重包。

## 双审与终态门

各新任务实际读回指定模型、思考等级、权限模式和task ID；ZCode=GLM-5.3/最高/yolo，MiniMax=M3.1-Flash/xhigh/bypassPermissions。完全访问不改只读审查职责。两个任务独立同版、不得互读本轮提示之外的另一模型报告/意见，不在提示中预泄露另一模型判断。只能各写自己的report，禁止修改代码/测试/配置/依赖/验收、切分支、stage/commit/push/PR/merge。禁止GUI/Electron/e2e/native/HMR、凭据/任务库/网络或新增付费；无变化不复测。

报告须给完整真实终态，列固定身份/实际model与mode、全文读取范围、每条可复现finding（优先级、准确路径/行、具体反例/影响和所需验证）、所有旧问题的独立核验结论、实际执行与未执行边界、剩余门、最后Pass/Fail/Blocked及原因。报告存在、文件名或界面模型名不等于完成；root需全文读回并处理全部意见。实际任务失败/中断/额度/路径错误如实保留，不由内部审替代或切换模型。

双方新同版真实终态通过与意见关闭后才可考虑push/PR；真实CI、正常develop合并/远端核验仍另行保持。正式文件选择、公共契约/错误/分页/bridge/App、正式Store/Job/worker/producer/selected和取消恢复、T02语义、T08/T10、两OS/真人、T03 FR-300–304及父57P0未由S1或本准备关闭。SQLite损坏HOLD及其他父级限制不变。
