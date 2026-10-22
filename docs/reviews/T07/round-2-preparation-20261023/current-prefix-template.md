# T07-S1 R2：双方全新完整工程重审（准备稿，任务尚未创建）

你将是 {{APP}} 的**全新独立完整审查者**。前一对任务已正式completed，但因流程失败及实际阅读缺项被记为 **PROCESS_FAIL**；历史作者的“限S1通过”原文保留，不能借用、续写为本轮Pass。当前不是只审delta、修复片段、最新7条意见或单项资源投影。完整S1仍含前六技术组成、25候选路径/14实现测试fixture、全部验收、PRD全文、历史首次失败/纠正与本次流程失败。

本段为当前操作要求；文末附旧完整143KB输入的原始字节，仅作完整历史/需求保留。旧文出现的旧workspace、旧报告、旧SID/turn、旧创建/静默状态或宽泛授权，均不能作为本轮路径/身份/写面/运行许可。当前正文不能被旧“最高权限”覆盖。产品/测试/验收/base并未变化，不为求绿改候选。

## 1. 精确身份与只读源

- 应用workspace和普通检查cwd唯一为 `{{ROOT}}`，detached reviewHead **fdfd908e36a85140078aa1509f091de369157973**。
- 批准base **5f910b52c69d86a1076b2032e5d3c63e715947f3**；产品/测试头 **f9a1157c2fff06c8bef17fa1ec44d8eb1ebacad3**。reviewHead只追加历史/过程证据。当前AGENTS由owner传播，唯一受保护M；不要stage、改写或混入。
- 全部tracked源和scratch副本的固定Git来源、逐文件身份见本方 `docs/reviews/T07/round-2-input/full-git-files.json`。25个产品候选的f9原字节另在 `{{RUNTIME}}/history/product-candidate/`；特别status.md是后继流程差异，不得宣称25项工作树全部物理等f9。代码/测试/fixture与f9不变。
- 本轮要求模型/思考/权限：**{{MODEL}} / {{EFFORT}} / {{PERMISSION}}**。这只是要求，不能预填为已核实际设置。
- **本次新任务唯一operator身份收据：`{{RUNTIME}}/metadata/operator-identity-receipt.json`。** 应由operator在创建时写真实本任务设置UI读回、fresh SID、原turn/附件受理等。准备模板为TEMPLATE_NOT_SUBMITTED、实际值null、任务0，不是实际审查回执。缺项标UNKNOWN并报告root；禁止为了定位身份自行 agent/list、agentlist、session get/sessionget、全session历史、globalconfig、.mimosa正文或任意全局恢复。不得find父项目/其他worktree/其他runtime寻找收据。给定路径缺失或不一致即记录，不扩搜；也不沿历史SID/turn恢复旧任务。
- 只读本方树、上述本角色runtime的已列历史/输入、固定base/product/reviewHead。禁止读取或发现性枚举R2另一方报告、目录、状态、队列、metadata或模型意见；本输入中封存的**前一轮已终态历史**属于共同历史输入，不是本轮peer意见。不读controller实时状态或凭据。

## 2. 完整读取与EOF门

先完整读取本条官方附件所有内容，连同文末旧完整输入；核附件bytes/SHA与本方 `round-2-input/input-manifest.json`，逐字等本方 `full-input.txt`。官方附件与本地文件须分别核实；小标题/hash、首次预览或“我已读”不能替完整接收。实际工具输出若截断，按实际最后返回行/字符继续到EOF，不能按请求limit推断已返回。hidden details全文、工具进程内部json.load、测试自动读fixture都不等于审查模型已看到全文。

然后逐项完成本方 `round-2-input/required-reading.json`：

1. **完整candidate.patch的全部25路径diff**，以及25项候选全文和14项全部实现/测试/fixture，不能只hash/keys/首事件/集合/计数。必须包含__init__.py、scenario.css、4963行t09-e5.json、530行round-projection-handoff.json及所有JSON字段。大文件分段Read可见全文，输出截断必须续读，不得head/tail/grep代替全篇。
2. 批准base的**完整PRD V0.6全文**，包括FR-700–705、附录C–G、D.1/D.2、E.1–E.5、G.4/G.6及第10–12节；同时读取原验收、接线提案、投影交接、12行父积压及当前指南。所有父能力未就绪事实保留，不把合成端口/三指标称产品通过。
3. 9条原始普通独审final与索引、IR-01～05全部首次发现/修复/关闭及首错；3条加密中间消息仅登记元信息，不解密或跟随sourceSession。旧42项READONLY证明失效，43/44是不同历史运行，不拼数或追认。
4. `{{RUNTIME}}/history/frozen-inputs/` 的75成员及其中**35个原始log/PNG原件**，按完整内容/真实图像读取并核archive-manifest的大小/hash；空日志如实记空，不能单独证明exit0。源码/规范/9条final等其他成员亦保留完整读取。禁止将35写成32或仅看日志head/tail。
5. 本文内嵌前一轮两完整作者报告、旧证据audit、原生补审、PROCESS_FAIL裁决、7项意见/责任/延期处置。再读取本树 `docs/reviews/T07/launch-20261023/native-receiving-20261023/` 中两方精确已封存tool-calls/tool-results及report-write-edit/官方终态/附件重建证据，按EOF核历史事实；不去原应用全局数据或旧review roots补采。原始JSONL长行必要时可按已知文件字符边界分段可见读取，不能因隐藏metadata可静态重算就称历史模型已读全。

在 `{{RUNTIME}}/metadata/reviewer-read-ledger.json` 逐项记录实际source/ref、工具call、**实际返回**范围、截断/续读与EOF、字节/hash。格式是证据索引，不是提前自签已读。压缩/compaction不能消除已丢证据。任一必读材料EOF不足、内容缺失、身份不符或必要运行未验，结论必须明确NotPass/未完成，并列缺项；禁止凭摘要或旧Z pass先写完整Pass。

## 3. 唯一写面与正常验证

- 唯一最终报告：`{{REPORT}}`（全文，用本任务Write/Edit真实写入）。禁止覆盖旧round-1报告、旧证据、冻结输入、manifest或原件。
- 允许新增取证材料仅在本方 `{{RUNTIME}}/raw/validation/`、`{{RUNTIME}}/reports/` 和已列 `reviewer-*.json` metadata；operator身份收据只读，模型不改。不写脚本包装验证命令。实现、测试、fixture、PRD、验收、配置、依赖锁、源码政策均只读，不commit/push/切分支。原正常检查的本树out/独占cache属于生成物，如实保留，不新增ignore或删除metadata求clean。
- 普通验证沿用原固定工程对应入口，可必要运行npm run check、原vitest/pytest、lint/typecheck/build/verify:sources；原套件含受控worker、临时SQLite、READONLY和os._exit回归，不能泛禁或冒称真实产品适配。**准备owner没有重跑任何无变化产品验证**。审者按工程审查需要运行，计数按实际，不以历史657/1142或90/27为目标自填。
- 每次验证直接运行原入口；完整stdout和stderr分别保存在本方raw/validation的全新文件，紧接目标命令记录其整数退出码、起止时间、argv/cwd与非敏感环境路径。不得使用 `| tail/head/grep` 作为原始输出或exit依据，不丢上游输出，不取管道末尾 `$?` 冒充目标退出。若工具自动截断，原文件完整保留并按offset/明确本任务返回路径取完，保持首失败与每次重试，不能覆盖同名原始日志。可在同一直接shell调用中将原命令stdout/stderr重定向到明确日志、紧接保存 `$?` 后退出同一码；不是许可创建脚本绕过拒绝。
- TMPDIR=`{{RUNTIME}}/tmp`；UV_CACHE_DIR=`{{RUNTIME}}/uv-cache`；UV_PROJECT_ENVIRONMENT=`{{ROOT}}/.venv`；npm_config_cache=`{{RUNTIME}}/npm-cache`；RUFF_CACHE_DIR=`{{RUNTIME}}/ruff-cache`；pytest基目录用`{{RUNTIME}}/pytest/`下每次全新子目录。清除ROOT_SOURCE_PATH/PYTHONPATH/ONTOLEARN_TEST_ENGINE/ONTOLEARN_DB_PATH等跨树覆盖，不打印全部环境或凭据。
- dev/HMR、Electron原生/test:e2e、engine:build/package:dir、产品启动/产物运行、新native/caller/producer/物理资源实验、真实模型/API、付费/重置不在本轮普通审查许可内；必要缺口交root精确裁定。当前GUI由主控调度，本任务不抢占、不CUA。

**任何工具自动审批/安全扫描/平台拒绝：保留原始命令、call ID、理由与状态；该项记未验并请求root精确裁定。不得换脚本、Write后执行、重定向改写、包装器、等价路径、不同工具或其他身份继续同一被拒目的；“可能误报”“Write成功”“完全访问”均不是解除。可继续独立只读审查，不得改报告把拒绝写成无首错。**

## 4. 可选合成页面探针：唯一精确scratch

固定review checkout禁止运行原render-probe，亦禁止从review cwd用绝对scratch脚本路径运行（process.cwd仍是固定树，这是前批真实违规）。

owner已准备完整固定reviewHead Git文件副本：`{{SCRATCH}}`，来源/逐文件hash见 `round-2-input/full-git-files.json`；除传播的AGENTS政策外，tracked文件精确等reviewHead。其node_modules是本角色独立物理副本，无跨角色共享env。旧副本ui-probe.json的before原字节在 `{{RUNTIME}}/raw/probe-before/`，旧PNG若未被Git追踪则明确不存在，不补造。

确需补验且无拒绝时，只能先在工具记录中明确 `cd {{SCRATCH}}`、核真实pwd，再以相对路径 `node docs/reviews/T07/evidence/render-probe.mjs` 调用**未修改**原脚本；不只改描述或脚本路径。不修改脚本/sandbox，使用已有授权Chromium；产物仅落该副本。完整stdout/stderr/直接目标exit留本方raw，保留before/after三件与副本身份。`.t07-ui-*`是脚本在该副本内的受控临时产物；只允许原脚本自身精确回收。模型不rm重建scratch或用旧产物冒充新运行。探针若不必要/不可运行，标未验及理由，历史合成页面证据不能提升成真实接线。

## 5. 本次输出门

报告须给真实operator任务设置与fresh SID/原turn（缺UNKNOWN）、完整Read覆盖/缺项、固定base/product/reviewHead及25/14来源、独立工程反例、每项历史Fail和7意见处置、实际命令/完整原始输出/真实退出/首错/拒绝及未验范围、P1/P2/P3和明确结论。无任何新工程P1/P2也不自动豁免过程失败或EOF不足。不得沿用前轮“无首错”或“完整14项通读”的不实笼统表述。

真实T05/T06、T01/I04生命周期/取消竞态/原子进度/终态/operation-id响应丢失对账、公共契约/bridge/App、删除/恢复/快照创建续跑、完整E5 facts/inferred/actionTrace/triggeredInstances、T10跨设备、父FR/附录验收、双OS/真人/CI/远端/发布门全部照实保留。双方均须各自全新完整审查与意见处置后才有后继门；不得自行发PR、改Goal或接收本轮peer意见。

以下是封存历史全文；仅本节以上新操作路径/边界适用于本轮。
