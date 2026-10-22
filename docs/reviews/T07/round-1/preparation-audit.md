# T07-S1 首轮准备包独立文档核验

结论：**通过本次过程准备范围，未发现需要阻断准备包的P1/P2。** 本结论不构成指定模型审查通过、T07运行租约或父功能验收。

审查者：新建独立agent `/root/t07_round1_document_audit`。日期：2026-10-22。审核提交 `f50ebc0fb9db792aceec103e623768d585a6175d`；工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-scenario`；分支 `feature/weekly-t07-scenario`。按 `audit-verify-explain-grade-5` 技能核对实际产物与直接证据。仅写本报告，未改其他文件、stage、commit或push。

## 实际静态核验

- 固定base `5f910b52c69d86a1076b2032e5d3c63e715947f3` 是产品/测试head `f9a1157c2fff06c8bef17fa1ec44d8eb1ebacad3` 的祖先。Git完整差异恰为manifest的25路径；逐项大小、SHA256与Git blob均匹配，candidate.patch逐字等binary/full-index差异，SHA256 `3e697c94bae835307e1012bb30ea65bbbce680555e488135bfcb267b4210b8a3`。
- 原candidate-files.json的14项与新manifest完整相同，当前物理实现/测试/fixture全部等固定f9。25项中24项物理等f9；唯一不同是后继流程 `docs/reviews/T07/status.md`，manifest明确标为false，README/提示词要求按固定ref读取，未混作产品变化。
- 准备提交相对982e453只新增本round-1的19文件。18项packet-files封存项逐一匹配当前文件及准备提交Git字节；packet-files排除自身与后追加审计报告的规则准确。核验时只有受保护AGENTS处于未暂存修改，没有被混入提交。
- 归档946863字节、SHA256 `880d4cc9b40587346919a178e3eaff5522aa9e65e49eab093307fa90da6748e6`；75成员无重复，完整成员名集合、大小、SHA均匹配。构成为25固定候选、4历史流程、35原始log/png、6操作/启动快照、4批准base规范及1份原始独审终态合集。35原始log/png集合与现有evidence目录精确相同，逐字等原件；固定Git成员与对应ref逐字相同。没有执行归档脚本或提取到产品路径。
- 9条原始独审final逐行SHA、实际message ID/作者/时间与源session指定行一致；合集SHA256 `51f5746a99cbeecacd15d0c6da0233586f25e1fa1821b662a65d2096c7be4361`。已全文读取9条原文，IR-01至05的发现/关闭索引有对应原始终态。3条加密中间消息只登记元信息，未解密。旧internal-review.md明确分类为开发者整理摘要，不冒称原始独立报告。
- 原始第7条明确早期42项中的READONLY假通过，第8、9条分别记录修复与44项交接复核。历史问题表、提示词和README未追认旧READONLY证明，未把不同专项拼成同次运行；空ui-identity.log限制及首错保留规则均已写明。

核验通过的命令类型为只读Git、Python标准库JSON/哈希/tar/source JSONL字节比对。首个提示词对比脚本使用过宽的全局模型名替换，误改共同政策中的另一平台名称，导致本审计脚本AssertionError；该错误不是产物缺陷。改为只替换任务标题、当前任务设置和自报告路径后，对比通过。除此之外，两次内容/归档核验均未运行产品代码或测试。

## 提示词及授权边界

两份提示词除应用标题、当前任务模型/思考/权限与自报告路径外内容相同，完整25路径/14身份未缩减。已全文读取共同任务正文与政策；规范化空白/表格分隔后，AGENTS、共同开发指令（含完整第九节）、默认权限三份快照内容完整透传，未遗漏政策文字。最新后台恢复快照另有明确全文读取要求。

ZCode为GLM-5.3/最高max/yolo，MiniMax为M3.1-Flash/xhigh/bypassPermissions；均要求逐任务实际设置读回。同base/head、双方全新完整独立任务、不互传本轮意见、只读实现、只写自己的报告、禁止GUI/HMR/commit/push等限制准确；真实任务终态、全文读回、原始final与来源hash、全部意见处置、变更后双新审及push/PR/CI/远端门均保留。

两份提示词和README明确当前租约属于T06、T07未派发、后台路线待本任务验证，不能沿用旧C2/昨日GUI许可或将T06受理当T07任务。读取的操作快照与其原文件逐字一致；旧“必须CUA/I05预约”由新说明显式修正。派发前仍须重读当时最新政策/租约，准备时快照不证明未来入口可用。

真实T05/T06、T01/I04生命周期/取消/原子进度/终态/operation-id响应丢失对账、公共契约/bridge/App、真实删除/恢复/快照创建/续跑、完整E5四类领域结果、T10跨设备、FR-700–705/E.2–E.5/G.4/G.6父验收和macOS/Windows平台/发布缺口均保留。维护交接未被扩大为采用未批准实现或启用schema/runtime。

## 本次未运行与限制

未运行产品静态检查、单元/引擎测试、构建/包、GUI/Electron/e2e/native/HMR、外部模型任务、登录/凭据、付费/重置或CI；未更改Goal。check657TS/1142Py、T07 90Py/27TS和headless结果只是原有证据，本次没有重测或重签其运行结论。本审计验证准备包的身份、完整性与文档边界，不重新审核产品算法，也不代替将来的两个指定模型完整审查。
