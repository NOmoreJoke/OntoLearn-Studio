# I06 metadata transfer guard core：独立审查与交付记录

2026-10-21，Asia/Shanghai。本登记的独立核心已实现并完成静默验证，未正式接线。原I06 Goal工具仍blocked，未重建/恢复/标完成；不将该模块当完整I06或X1–X6通过。

## 固定候选与范围

- worktree：/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-transfer-guard-core；branch：feature/I06-transfer-guard-core；批准base：5f910b52c69d86a1076b2032e5d3c63e715947f3。
- 登记SHA：4ea82f5408a3d4d15b06cb853905f96902182a275d5d4ec503567192f31ffac8；总控独立设计审查：abeece37c930c5353b4ab78bf75de575a43e74a87c518f3dcb1a783b4607deeb。
- AGENTS当前78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759保护未暂存；common ff5f9fd0a4913cc6c2fa612ec565bdf40d67db4a6640e5293d4ca1e7d02cfaff。独立npm ci/uv sync，Node24.15.0、Python3.12.12；没有复用他线可变依赖。
- 唯一产品文件：apps/desktop/src/main/security/private-root-transfer-guard.ts，SHA3159cecdd3b6542b58b841b1f445662bc09381cb9ca63cf670980aa978da7da4。
- 唯一测试：tests/unit/i06-transfer-location-guard.test.ts，SHAeb73497a50dde4ff0c455f98b08d6cb41df4b6b2609323ca6157e5a1381a26fe。
- 合同：[transfer-guard-core-v1.md](../../iterations/I06/transfer-guard-core-v1.md)，SHAad67e4e1837a6f630c3f5980f2add3e3bb8e9444a60071bb6c6e7e05e2b18879。

原I06/e2c树及任何既有产品/测试/依赖/锁/CI未改。本新树未复制未批e2c/C3或source_content实现。产品没有导入本模块；生产build只证明现有应用构建，新增模块本身由TS类型检查/专属单测实际覆盖。没有FS action/wrapper/lease、真实平台adapter、metadata库存owner或任何新公共接口。

## 独立设计审查

/root/i06_design_review实际只读登记、总控设计报告和v1合同。初稿要求sourceRead/unpack必需，与无附件导出/无需解包合法none冲突；已修为export只final必需、import inputPackage/newProject必需，sourceRead/staging/unpack按用途显式none。另明确捕获惰性副本后Zod不重读原对象、anchor+suffix总深度32、规范device/inode串及root自身identity保护。审查输入修订SHAe8bb28604fcc9776ac17a5d048d5b59fbccbb178079405a0f4ea63dc11c0079d，原意见关闭后才实施。

/root/i06_interface_docs另只读提出8组必要反例，已实际读回ff5/78df：scope ABA/同步abort重入、保护视图vslocations分层、未settled两槽、revision倒序、metadata绝不授IO、路径/物理别名分开、复制和资源期限。两agent均未争写新树或执行产品。

## 实现审查：3项P2与实际红绿

独立实现审查者仍为/root/i06_design_review；仅静态读取固定模块/测试，不运行产品、不代替指定双审。首版模块SHAe342d2b84672f578efc6e04f0d99059bbd6c0473decdf3f4a5f6d256a5cc0790；原件[review-red-module](transfer-guard-core/review-red-module.ts.txt)保留。首批51项通过不足以覆盖下面缺陷，未沿用为最终通过。

| 发现                 | 真实失败与修复                                                                                                                                                                                                     | 最终独立结论 |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------ |
| P2 捕获期间同步重入  | owner metadata Proxy可在capture中open新request，旧evaluate仍安装candidate。新增旧版反例确实收到metadata-eligible；修为捕获/parse后在保护revision写入前核原request，并在最终安装/revalidate前再次核context/实际时限 | closed       |
| P2 未知异常二次逸出  | failure使用instanceof，对抛出的Proxy可再触发getPrototypeOf并逸出合成私有路径Error。旧版实际promise reject原异常；修为仅内部WeakMap标记reason，未知throw不检查属性/prototype，固定invalid                           | closed       |
| P2 硬时限仅timer不足 | 同步owner返回前clock已过5秒，Promise微任务可先于timer成功；capture本身越30秒时还使用旧time。两独立反例旧版均实际eligible；修为观察返回、捕获校验后均核5秒deadline，安装时重核30秒，revalidate同等处理              | closed       |

原[全54测试红日志](transfer-guard-core/unit-review-red.txt)：3failed/51passed；增加同步owner时限反例后[定向红日志](transfer-guard-core/unit-review-deadline-red.txt)：4failed/51skipped，skip是定向选择，不能计通过。两份当时测试快照保留。修复后[专属结果](transfer-guard-core/unit-review-fixed.txt)：55passed/0skipped/exit0。

独立最终定点复核实际核3159/eb7349/ad67三SHA、旧模块快照与上述原日志，确认3项P2全部closed、无新增静态阻断；未自行重跑，未改文件。5秒是超时结果分类，不声称可以抢占恶意/阻塞同进程port或证明CPU隔离。

## 实际验证

| 命令/范围                                  | 工具实际终态与原件                                                                                                                                                           |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| npm ci / uv sync --frozen                  | 各exit0；新树独立node_modules/.venv，见专属原件                                                                                                                              |
| npm run check                              | exit0；685TS（含本线55）、1052Python；lint/format/typecheck/build/ruff全部通过，[完整日志](transfer-guard-core/check-final.txt)                                              |
| npm run verify:sources                     | exit0，12归档源文件一致，[原件](transfer-guard-core/sources-final.txt)                                                                                                       |
| 初次desktop typecheck                      | exit2，局部toSorted超ES2022目标；改局部复制sort，不改配置/依赖，原日志保留                                                                                                   |
| 初次专属ESLint                             | exit1，测试prefer-const；仅修局部声明，第二次通过；完整check已覆盖                                                                                                           |
| 最终docs/JSON定向格式、暂存diff与路径/hash | 提交前核对；源码/测试/合同/非raw证据通过。6份原生txt日志保留其末尾空行，完整cached diff-check对这些原件报blank-line-at-EOF；不改原件消除提示，不因纯证据追加重跑未变运行矩阵 |

小型原始CLI日志和红版源码/测试快照为复核上述实测失败所必需，按登记专属目录入库；不含真实凭据、业务内容或运行DB。测试中的private/secret字符串均为明确合成反例。artifact-manifest.json给出逐文件字节/SHA与命令终态，不用文件数代替验收。

## 当前能力及未完成边界

实现严格descriptor/none、有界惰性捕获、完整根/前缀/活动及退役identity冲突、owner观察副本与保护revision、本厂对象身份request/token、有限在途/期限/撤销/释放/关闭与跨await本地fence。终态释放大视图；abort/timeout不提前释放实际未settled观察槽。不同owner实例不共享库存权威，模块不扫描内容或持久维护inventory。

metadata-eligible仅限给定port观察的本地候选；check是as-of本地状态，revalidate不是外部原子FS fence。port本体仍为可信main依赖假设，不认证OS来源或隔离其任意JS副作用。contentIo恒unsupported，不接收或调用consumer/action，无allowUnsafe/testRuntime工厂。无真实owner/FS时生产消费者零调用；既有Store完整单测通过不等于已做T10真实转移/Store组合联验。

实际metadata owner/退役/锁、平台身份与FS能力、main/T10/T01接线需总控另精确登记；同UID namespace原子confinement、Windows/macOS真实能力、秘密DLP均不在此核心。未运行GUI/Electron/e2e/native、凭据、付费API/server或容器，没有push/PR。原X1–X6、同完整候选指定双模型、CI与完整父门保留。

上游T01 r3/T10固定设计及总控来源r3审查已全文读回并核SHA，接受精确同块幂等的活状态限制、终态不伪造ack、稳定plan/临时admission及旧claim先授权分流；256attempt/256MiB仅按总控技术采用记录，不冒充实测。详见[读回记录](transfer-guard-core/upstream-interface-readback.json)，不将这些来源合同或其代码混入本guard实现。
