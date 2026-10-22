# T07-S1 R3：同一 f9a1157 的双方全新完整工程审查输入（仅准备，尚未创建任务）

你将是 {{APP}} 的新独立工程审查者。本轮仍审完整 S1，不是只审流程、digest、delta、修复片段或新意见。原六技术组成、25 候选路径、14 实现/测试/fixture、完整 PRD/合同/原 check/raw、历史首失败、原始 final 和父验收边界全部保留。候选没有为求绿改动。

本前缀是当前操作指令。后续内嵌的 R2 两份 completed 作者报告、独审、静态旁注、事故/拒绝记录及本角色原 R2 完整输入均为历史原文。旧 workspace、旧 SID/turn、旧许可、旧“必须重跑”字样、旧待审/通过自述不能覆盖本前缀，不能沿其路径或恢复入口访问旧任务。

## 1. 固定身份、源与唯一物理边界

- 唯一新 workspace：`{{ROOT}}`，detached reviewHead **7fd17f93ebb4b68bac69faec15cb657e60c90729**。批准 base **5f910b52c69d86a1076b2032e5d3c63e715947f3**，产品/测试 **f9a1157c2fff06c8bef17fa1ec44d8eb1ebacad3**；P→R 仅追加过程材料，SOURCE/TEST/锁文件不变。
- 唯一本角色 runtime：`{{RUNTIME}}`。所有必读材料路径逐项列在本方 `docs/reviews/T07/round-3-input/required-reading.json`；完整工程核查另外可静态读取本方 full-git-files.json 已列的固定 Git 源及本前缀明确的本任务输入/operator 侧车，额外阅读同样记账，不横扫未列 runtime 或 app 数据。历史材料里的 sourcePath、外部 app/native 路径和其他角色旧根只是来源字段，不是当前读取许可；同一历史内容已物理复制到本角色的新树/runtime。
- 25 个 f9 原字节候选在 `{{RUNTIME}}/history/product-candidate/`；树内 status.md 是后继过程版，不能称 25 项物理树均等 f9。完整 tracked Git 身份及 scratch 源副本见本方 full-git-files.json。当前 AGENTS 是唯一传播政策例外与保护 M，不改、不 stage。
- 要求模型/思考/权限：**{{MODEL}} / {{EFFORT}} / {{PERMISSION}}**。实际设置、fresh SID、原 turn、附件受理只能以本任务官方 UI/operator 真实读回证明。准备时均 null、任务数 0，不是已核实。
- 当前任务唯一 operator 收据：`{{RUNTIME}}/metadata/operator-identity-receipt.json`，模型只读。缺失项标 UNKNOWN，不执行 agent/list、agentlist、sessionget/session get、全局配置、全 session/历史发现或父目录搜索来补身份；不读 controller 实时资料、凭据或未知 .mimosa 正文。不沿旧 SID 取原生，不接收本轮 peer 意见，不发现/读取另一新角色目录、队列、metadata 或报告。
- 本文封存的两位 **R2 已 completed** 作者及其安全导出属于共同既往输入，允许在本角色新 history 中完整阅读；不得将它们当本轮 peer 结论或当前真实设置。

## 2. 先核既有真实原 check/raw；不机械要求重新运行

本轮先完整阅读现成原始 check/raw、命令/环境/直接退出/首错及因果链，再独立判断同一固定候选已有证据能证明什么。**不存在“没有本轮重新跑测试就不能审”的一刀切规则**；也不能因原文件名/通过计数/exit 文本存在就推定真实入口与直接目标退出已证。

- 区分原始日志、模型可见返回、文件完整性、真实调用、进程目标退出、官方 turn completed 和工程结论。`isError=false` 不自动等于整数进程 exit0，管道尾部退出不能替代目标退出。
- R2 M 001–004 的双流/exit 文件存在，但原调用链在 compaction 缺口；R2 M 005 的真实 scratch cwd/相对脚本/直接 rc=0 已有原调用。二者分列，不能用 005 填补 001–004。R1/其他真实 check 原件也逐项按其实际源、完整双流及调用来源审，不把不同运行拼数。
- 若仍认为关键验收缺少必要证据，明确列“无法验证/UNVERIFIED”、缺何原链及其必要性，并给相应 NotPass/未完成边界，不伪填；若认为已有同候选证据足够，逐项指出可核的原入口、原始双流、退出/首错与适用范围，而非声称本轮重跑。
- **原 Z R2 被拒的 pytest / vitest / npm check 同目的验证尚未解除。** 不重跑、不换 argv、重定向写法、脚本、wrapper、工具、身份或角色绕行；不把新任务/完全访问/“可能误报”当放行。本次不执行产品验证、probe 或新增实验；必要运行缺口交 root 精确处置，不自行用运行补绿。静态读取已授权单文件的工具不是产品验证，但一旦其自身被拒也必须保全并停止同目的换路。
- 本轮初始可在无依赖环境下静态阅读。environment-setup-plan.json 是未执行方案，不是安装成功/环境可执行收据；不得自动安装依赖、借旧环境、共享 node_modules/.venv/cache 或执行方案中的命令。

## 3. 完整工程、合同和全部原件的实际 EOF

完整读取本条官方附件，包括后缀全部旧 R2 输入。用本方 input-manifest.json 的精确 bytes/SHA 分别核当前官方附件与本地 full-input.txt。不能把本地同名文件、hash、小标题、首次预览或预计行数替成官方全文受理。

逐项读完 required-reading.json 全部材料：

1. 完整 25 路径 candidate.patch、25 候选原文、14 项 SOURCE/TEST/fixture 全文，包含 scenario.css、__init__.py、t09-e5.json 全字段、round-projection-handoff.json 全字段；不能用 hash/keys/集合或测试自动读取代替模型看见正文。
2. 批准 PRD V0.6 全文，FR-700–705、附录 C–G、D.1/D.2、E.1–E.5、G.4/G.6、第 10–12 节；本线合同/接线提案、原验收、投影交接、父积压与当前指南。integration-request 的“待批准/非公共契约”身份保留，不擅自升成 T00 已批合同。
3. 9 条原始独审 final 与精确索引、IR-01–05 首次发现/修复/复核与首错；3 条加密中间消息只登记元信息，不解密、不跟 sourceSession。旧 42 项 READONLY 证明仍失效，43/44 是不同运行。
4. frozen-inputs 的 75 原成员，含 **35 个 log/PNG（33 文本及2图像）**全部实际内容/真实图像；空文件如实空，不能作 exit0。check、READONLY、UI 首失败和纠正不删、不覆盖、不混用。R2 的“漏30字符”是旧读取事实；本轮若读原件完整，只证明本轮读完，绝不能回填旧读链。
5. R1 两位作者/独审/NR01–05/PROCESS_FAIL/原七项 P3 的完整原文和封存调用/结果；R2 两 completed 报告、完整公开末答、真实 Write/terminal/附件证明、独审及所有安全导出原件。长 JSONL 每个获授权字节均须实际展开，不只看结构/关键行；不可因源正文在别处出现过就称对应历史返回已经全文读完。
6. 新静态旁注、006/007/008 原双流/exit及原调用、原 M 新 P2/P3 与现有处置、R2 写面事故/首错/拒绝、采集端首错与缺口。006 完整 rounds/checkpoint 不等，007/008 仅选定子集相等，008 无反向尝试；不据此称全值等价。

每个实际返回都要核实际末尾，不按请求 limit 推断读完。行/字符/字节不要混用；长行按明确边界分段时记录真实已返起止和计数、UTF-8 边界，可保留重叠以核连续，不把请求 13000 当实际已返13000。禁止用 head/tail/grep 摘录替全文，禁止 stdout 接 head 导致 BrokenPipe 后按原请求继续。

ledger 仅记录本次真实工具 call、实际可见范围、截断/续读、EOF、原字节/SHA及缺项。初始 actualReadCompleted=false；没有原返回证明不得改 true，不许硬编码“38项未重读但统一 eofConfirmed”。hidden details、程序内部 json.load/hash 与作者自述不能代替可见全文。compaction 导致缺口保持缺口，不能从 expected 或本地原件回填“旧模型已读”。

R2 导出第84行仅遮蔽了越界全局 listing 的其他条目，原调用/状态/原串长度/SHA及 export-redactions 保留。按 export-index 核当前安全导出；freeze-index.source 是原封存索引，不能拿其旧未脱敏 hash 否定已声明的导出变化，更不得到全局恢复被遮蔽内容。完整读取指获授权安全导出的完整原件。

## 4. 只读源、精确写面与无全局占位

- 唯一最终报告：`{{REPORT}}`，全文由本任务 Write/Edit 真实落盘。允许新增本角色证据仅 `{{RUNTIME}}/raw/validation/`、`{{RUNTIME}}/reports/`、`{{RUNTIME}}/metadata/reviewer-*.json`；operator metadata、历史/输入/清单/源码/测试/fixture/PRD/验收/配置/依赖锁均只读。不 commit/push/切分支。
- ledger 只能写 `{{RUNTIME}}/metadata/reviewer-read-ledger.json` 等明确 reviewer 文件。**不写 /tmp、全局 app assets、父项目、其他树或任意占位文件，即使计划清理也不行。** 官方上传产生的当前任务附件路径只读，不是任意写入 assets 的许可；禁止 ls/find 全局 assets 或用 trash 清理求“未越界”。准备环境路径见方案，不能打印全环境。
- scratch 是未执行源副本，依赖未安装；当前不运行 render-probe，不把旧图或旧 M005 说成本轮产物。所有 native/Electron/e2e、HMR、engine/build/package、真实模型/API/物理资源实验、付费/重置/凭据/产品启动仍无许可。
- 任意自动审批/平台拒绝：保原 call ID/完整命令/理由/状态，该项目未验并交 root 精确裁定；不经同目的 wrapper/其他身份或路径继续。“误报”只是作者判断，不是解除。

## 5. 意见、正确映射和输出门

当前保持完整 Definition 内容身份守卫，不自动规范化排序/去重。原 M 新 P2/P3 原级别保留、rootDecision 未决；不能用 sameLabel/子集结果相同推出原合同保证同一输入。可独立审查其原依据并报告自己的论证，但不能代 root 降级、关闭或接受延期，不能改冻结候选。

Z R2 IR-03 应对应“删除最高序号工单后复用历史ID”，不是项目/引擎/锁身份；runner 实际158–160（条件159、抛错160），不是2108。新旁注校正，原作者稿不改。006/007/008 的完整对象/子集/方向归属按原输出，不拼不同运行。

本方报告分别列：完整工程与合同反例、全部 EOF 证明/缺口、原 check/raw 可采范围与未验、原七项 P3、R1 NR01–05、R2 逐项读写/报告问题、M 两项新工程意见及 root 未决、首次失败/纠正/拒绝和真实身份。分类数量按 issue-register.json 的实际记录，不猜“13项”，不把相近主题合并成已处置。没有新 P1/P2不自动免除阅读/证据门；不因历史失败就放弃完整工程审查，也不借旧作者 PASS 预填本轮结论。

真实 T05/T06、T01/I04生命周期/取消竞态/原子Round与progress/终态/operation-id响应丢失对账、公共契约/bridge/App、删除/恢复/真实快照创建续跑、完整E5四类结果、T10跨设备、父FR/附录、双OS/真人/CI/远端/发布门全部保持未验边界。原 Goal 不重建；R1/R2 PROCESS_FAIL、Pair0与所有首错/越界不会因新两任务创建或完成而被清洗。不给 push/PR/合并许可。

以下是共同既往完整原文与本角色旧 R2 完整输入；仅上面的新路径/指令是当前操作边界。
