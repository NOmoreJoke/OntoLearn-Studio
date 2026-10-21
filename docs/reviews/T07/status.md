# T07 沙盘状态

2026-10-21，owner：本功能聊天 `01a15bce-0706-7360-8e99-df8fe9b15ad2`。

- 实查 worktree：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-scenario`。
- 分支：`feature/weekly-t07-scenario`；base/初始 HEAD：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- AGENTS SHA256：`db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`，仅保护文件有既存未暂存改动，不提交。
- 已建立独立 Goal；阶段：独立实现及私有验证通过（private_implementation_validated）。没有正式接线、父功能完成、外审或发布通过证据。
- 独占路径：`packages/engine/src/ontolearn_engine/scenario/`、`packages/engine/tests/test_scenario_*.py`、`apps/desktop/src/renderer/src/scenario/`、`tests/unit/t07-*.test.ts`、`tests/fixtures/scenario/`、`docs/reviews/T07/`、`docs/iterations/T07/`。启动时这些路径无既存冲突。
- 范围：FR-700–705、E.2–E.5、D/G.4/G.6 与全部原父功能跨模块验收保留。
- 下一交付：总控协调批准T05/T06/T01/I04与T00精确接口后正式联验；同时可安排本私有子集同候选指定审查，保留完整父功能门禁。
- 验证：`npm run check`、专属 Python/vitest；不运行本机 Electron/e2e/HMR/native 或凭据提示。未引入新依赖，不触碰归档源和打包配置。
- 共享缺口：T05 实际推理快照、T06 冻结计划/冲突/执行接口、T01/I04 原子逐轮提交及取消门、T00 contracts/bridge/UI 挂载；具体提案见 `docs/iterations/T07/integration-request.md`。未批准候选不消费，不新建公共契约/可变存储/网关。
- 外审：启动时ZCode/MiniMax资源预约属于I05；最后只读调度记录显示T06-S1下一预约、I05-C2后续排队，本线未取得资源也未自行操作。指定双方新任务、同候选完整通过、读回处置之后才 push/PR；实际 CI 和正常合并/远端核验未执行。

## 本轮独立实现进展

- 服务与页面已实际实现；普通独立内审通过，4项P2逐项修复并独立关闭，见 `internal-review.md`。
- 新增独立测试：Python46项、TS27项；专属E.5核对两种产能全部创建/完成/积压/消费/指标集合并各重复重放两次。
- headless Chromium `151.0.7922.34`（已有cache revision1234）实际验证1440×1100与390×844；显式启用Chromium sandbox，无Electron、无HTTP服务/模型。确认历史标识、未处理事件、错误脱敏、文字转义、资源换算、自定义输入、非法事件禁用、已有场景仍可从基准项目创建。页面证据不是正式业务接线验收。
- 首失败保留：ruff首跑格式问题；页面首跑缺少Playwright匹配浏览器；新增select的精确标签定位超时，改显式aria-label后通过。原始日志/截图保留本地，摘要/哈希入库。
- AGENTS的M0计划路径在批准基线缺失；实际读取同版 `docs/reviews/I03/inputs/m0-review-and-update-plan-2026-10-19.md`、ADR-0001与ADR-0002，未改共享指南或归档源。
- 实际接收总控第九节/无桌面全文补充；共同指令SHA实查为 `9717f699e14b5941e15d90269f33cbebc32ef9bec6e7439739be848753419880`。给定第九节SHA `1f57a08e909e9d49a6e2c2d6e7012beec3e22b8e3c9e8eacad22c84dfb2d4b54`、无桌面段SHA `5215df2ead4745e7d74f137c4fa6ac837a54114590b5dee2d83cd16bb728551d` 作为透传记录，没有伪称独立提取复算。已向内审agent同步；原Goal不重建，无额度告警/消费重置/付费/GUI操作。
- 已实际向总控发送启动与政策回执；尚待批准接口与外审资源安排。Goal保持active，未将完整T07/发布标完成。

- 最后自查补齐项目ID、引擎版本和依赖锁身份；均参与输入摘要/恢复与页面比较，跨项目/实现不允许续跑或标当前。真实服务适配器仍需绑定项目/输入版本并由唯一公共契约复验。

- 实际接收并读取ZCode/MiniMax默认执行权限全文与仓库外权限证据；最新AGENTS SHA实查 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`、共同指令 `df09014af4d6cf757ca0977a995497f3646cd330e8921710876663a40a8cbcb4`。AGENTS由总控追加且继续未暂存；已向独立agent透传。默认yolo/bypassPermissions不改变只读职责与原门禁，不因纯政策更新重启Goal/计算或无变化重审；本线未操作应用配置。

- 按总控新批准只读取得T09固定提交 `873c8c051b9870aa12fc7e1dbbd3e0c358e7c380` 的输入；manifest SHA `aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e`、PRD源及17项文件哈希全部逐项匹配。仅在本线保存原字节manifest/E.5，未消费T09服务或Store helper。新增两产能资源/指标投影测试，工单完成不闭环告警，未闭环高危为4/8/12/16。断言完整工单身份/状态/创建轮、资源集合、消费与未来事件；facts/inferred/actionTrace仍待真实T05/T06验收，不将投影子集称为完整G-list通过。

- 接线前自查补充显式轮次/阶段Context及推理阶段身份，续跑不依赖适配器计数；持久Round含逐动作actionIndex完整轨迹及冻结计划，缺失/重复轨迹拒绝执行。已新增正反例并请求独立完整复核。

- 最终当前源码`npm run check`实际退出0：657项TS、1098项Python（本线46项Python/27项TS）、lint/格式/类型/构建/ruff全部通过；12归档源校验通过。验证摘要及本地首失败/最终日志哈希见`evidence/validation.json`；源码/测试精确哈希见`evidence/candidate-files.json`。没有Electron/e2e/打包/生产证据。

## 本地恢复点与下一步

- 实现候选本地提交：`791a7b2b9ea831105e3aa7ef2e95f80001942ba5`；base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。提交后源码/测试与候选哈希一致；未暂存仅总控保护的AGENTS，产品路径无未提交差异。
- 当前仍未push/建PR/执行CI/合并，未操作ZCode/MiniMax应用；父功能Goal保持active。普通内审不替代原指定双审。
- 下一步按总控批准的精确依赖逐个接入，不等待整个M0：T05推理快照、T06事件/冻结计划/动作、T01/I04原子轮次/取消/恢复/用户删除生命周期，T00契约与页面挂载；每个实际版本联验后刷新批准develop和最终候选。
- 本恢复点可供独立服务子集预约审查；完整T07验收继续包含真实E.5事实/推导/轨迹、跨设备重放及FR-700–705原父功能所有跨模块验收，不以服务子集合并关闭父任务。

## Goal续跑：真实Store边界与T01固定交接

- 上一轮为实际进展：独立实现/验证/内审及本地恢复提交完成；本轮开始重新核验worktree、批准develop、owner与官方总控live句柄。无新批准T05/T06实现，未消费其变化候选。
- 新增`test_scenario_persistence.py`：runner实际生成完整Round，在临时真实SQLite落盘并重开；两产能完整载荷，0/1前轮×5阶段×取消/异常/真实READONLY，10个真实子进程os._exit，以及负对照与交接JSON一致性，专属44项通过。与原轮次46项合计90。未新增产品Store写入通道。
- 独立agent发现新P2：READONLY注入失效后的Assertion可能被runner吞掉。已在runner外逐例断言真实OperationalError和SQLITE_READONLY错误码/名称；禁用注入的负对照拒绝假证据。独立复核关闭，首失败及旧证据日志本地保留。
- T01四Python交接已由总控正式生效并全文读取agreement；本线不改共享。固定`integration-request.md`与`round-projection-handoff.md`及完整JSON样例，明确test.rounds toy限制、唯一owner、完整Round/Checkpoint、事件范围、固定operation/expectedRound和响应丢失原marker核对；已实际发总控按T01路由。
- 独立只读普通内审确认当前新增持久化/投影子集通过；生产Store/JobStore与批准5f字节匹配，没有采用新owner未批准代码。正式I04/领域/终态/跨设备和指定双新审/CI/合并仍未通过。

- 本轮修复后最终`npm run check`实际退出0：657项TS、1142项Python（本线46轮次＋44持久化＝90 Python；另27 TS）。当前新增测试与完整交接样例已普通独立内审通过，生产/共享源码未变。摘要、源字节和固定交接哈希见`evidence/persistence-validation.json`；旧READONLY首跑通过不再作为真实故障证据。

## 指定审查准备证据

- 本轮重新实查远端及总控批准develop仍为5f，本线源码/测试候选f9a1157、25项完整提交差异的授权范围与实际工作字节、manifest及最终原日志哈希全部匹配；未做无变化测试。准备包见`external-review-readiness.md`及JSON。
- 仅保护AGENTS有既存未暂存变化；外审未启动、无应用资源lease，T06-S1后I05-C2仍由总控排队。准备包不代表双审通过或父功能完成。
- 已读取共同指南最新责任段SHA b24c4c88404f422c5fae4bf6c01e231b678e46741250801e8100cc62a31fec39及T01 canonical/main8已生效协议，并向本线agent实际透传。AGENTS仍78df2825…a759。T01新增共享责任不授权本线改文件或消费未批代码；旧冻结政策和固定T01提案字节保留，不因此重建Goal/无变化重测。
