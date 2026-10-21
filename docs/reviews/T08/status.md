# T08 状态

## 启动回执（2026-10-21，Asia/Shanghai）

- 聊天/Goal：`01a15bc2-40dd-7393-a1cb-1e87086e6993`，独立 Goal 已建立，active。
- 工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T08-agent-model`。
- 分支：`feature/weekly-t08-agent-model`；批准 base / 初始 HEAD：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 初始 git 状态仅 ` M AGENTS.md`；受保护 SHA256 为 `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`，与要求匹配，保持不暂存。
- 初始新增责任路径无 tracked 文件冲突。仅使用 main/agent、renderer/src/agent、t08 单测、fixtures/agent、reviews/T08、iterations/T08；不修改公共契约/网关/接线/锁/CI/Python或总控 state/tasks。
- 已全文读取启动提示、共同指令、decisions、T11资源预检、controller handoff、plan、review、T08任务及需求/验收条款；PRD FR-800–806/900–902/904、11.3/12.2、C/D/F/G.5，以及架构ADR。旧指南中的架构计划路径已不存在，改读批准树的 docs/reviews/I03/inputs 对应归档。
- 当前工作：独立纯协议 codec、白名单/受信上下文/草稿与可信回答、版本化合成评估。下一交付：可执行输入/完整预期、必要check、独立agent内审和本地可恢复提交。

## 验收与未验边界

原 FR、A-01–05/09/10、11.3/12.2 均保留。合成协议/纯服务测试不构成真实API、真实领域工具、页面或父P0验收。

计划无窗口执行 npm run check；独立内审。main变更要求的e2e仅可在已预约隔离环境执行，本机不启动Electron/e2e/HMR/GUI或凭据提示。

仍需批准I06唯一安全传输、T01项目/ChangeSet与撤销、T02–T07真实工具、T00公共接线；API主体权限/消费硬上限尚未提供，不读取secret、不调用真实服务。指定ZCode/MiniMax资源当前I05占用，最终同候选双方全新审查仍待总控预约。未push/PR/合并。

## 独立实现交付（2026-10-21）

- 可恢复实现候选：`9bfd3105a2f847771d8039b93e6615fa94c4fdfa`，本地提交，未push。
- 已实现：严格文字/非流式DeepSeek Chat Completions codec、完整thinking工具多轮字段和ID关联、白名单和参数整批预验、获批领域端口缺省不可用、可信上下文/迟到隔离、版本化待确认草稿、完整真实工具收据展示、有限教育提示、结构化/工具/评估与漂移分开的能力判定，以及每页最多4个动作/离线策略纯函数。
- 版本化合成基线：manifest.v1 + 13份完整输入/预期，T08共49项定向回归。它只验证协议/调度/证据忠实性，未实际执行查询/推理/沙盘；真实11.3/12.2/A系列仍待接线验收。
- `npm run check` 最终exit0：18个TS测试文件、679项测试，Python1052项，lint/format/typecheck/build/ruff通过。`npm run verify:sources` exit0，12份归档一致。摘要及固定候选文件哈希见 evidence/verification.json。
- 首次check因新工作树缺少`.venv/bin/python`，8项既有task-runtime测试ENOENT；已用`uv sync --frozen`建立本树独立环境。原失败全文保留evidence/check-first-failure.txt.gz（入库理由：保留首次失败环境审计证据，仅合成数据，原始23KB，gzip保留逐字节内容），不将首跑改记为通过。`npm ci --ignore-scripts`未改依赖锁。
- 内审1明确不通过：发现自由回答隐藏失败、工具ID校验不一致；已修复并新增回归，原意见见internal-review-1.md。固定候选的独立修复复核已明确通过（原P1/P2关闭、3文件49项独立测试通过），见internal-review-2.md；这不是指定双模型外审。
- I06/T01/T00精确接口、版本/取消/预算/字段溯源需求见 [design-and-integration](../../iterations/T08/design-and-integration.md)。当前不消费未批准代码，未新建网关/项目权威。

本轮完成纯服务独立实现与本地预验；T08父P0、Goal仍active。main纯模块对应的e2e待预约隔离环境；页面/正式API/所有实际领域工具/安全存储/最终字节授权与最小外发记录/原子Diff撤销/目标双平台/同候选指定双方新审/CI合并均未验。下一步按总控批准接口和资源预约接线并留在本聊天完成原门禁，不因局部完成关闭父任务。

## 第二批：纯会话往返与恢复边界（2026-10-21）

- 当前固定实现候选：`af9e59f7ce856521e751fcf23f417fdd3377e2da`；此前9bfd310首批候选保留。仅在原T08私有路径继续，无共享实现/锁/CI/总控状态改写。
- 新增conversation状态机，实际串起严格codec、白名单真实端口、工具返回字段最小化、后续请求和真实证据答案；只准备数据，不发送网络、不授予授权。覆盖交换ID/响应ID防重放、并发拒绝、完整thinking字段、多用户轮次、预算和取消。
- 同问题内完整收据不可隐藏；新问题不自动复用旧成功，全会话tool ID与预算仍保留。模型失败、预算耗尽及批次取消时，本轮已完成草稿/证据从只读克隆localReceipts保留，并附原inputContext。实际页面持久草稿与领域任务状态仍待T01/I04/T00接线，不把内存会话当项目权威。
- 独立内审3/4分别发现跨问题旧证据、最终模型失败后草稿不可读；原不通过报告保留。修复后固定af9e59f的独立内审5明确通过，4文件61项定向通过；原所有历史问题逐项关闭。
- 新固定候选完整check已exit0：19个TS测试文件691项、Python1052项，lint/format/typecheck/build/ruff通过；证据与固定文件哈希见evidence/verification-af9e59f.json。未重复执行无改动来源检查或本机e2e。
- 依赖复核：总控execution-state更新于2026-10-21 08:42:42北京时间，批准develop仍5f910b5，共享归属不变，T00仍提案、指定审查资源仍归I05，真实DeepSeek权限/消费上限仍未落实；没有可消费的新正式接线批准。继续保留全部真实API/领域/页面/最终授权/外审/CI合并门禁。

## 第三批：私有侧栏与完整上下文（2026-10-21）

- 固定实现候选 `3a4c2ea29da12afe2a4f2e8f8504331e9f8cf967`，本地可恢复提交，未push。新增AgentSidebar.tsx、专属CSS和呈现纯函数；未改共享App/style.css/preload/contracts或锁文件，未接入模型设置或另建授权。
- 组件显示受信上下文、最多4个页面动作、真实工具记录/引用、失败/过期/历史/取消、草稿详细建议及版本基准；真正Diff入口仅经显式宿主处理器且检查基准，组件无确认或正式提交。完全本地/未就绪/缺处理器禁用模型发送和模型重试；已存在本地处理器才可执行本地动作。输入不因发送或失败清空。
- main会话state.inputContext扩为完整TrustedContext的克隆，UI比较含有序选中对象/module/mode，与main语义一致；旧上下文动作/预览禁用，嵌套数组不可反写主会话。回调异常固定化，异步dispatch同步防重入。
- SSR实际编译并渲染组件，覆盖HTML文本安全及无资源注入、001/0/false/null、所有结果状态、失败保留记录、模型重试本地禁用、缺handler禁用、旧基准及选中/module/mode变化。T08目前5文件76项通过；内审6原不通过及修复保留，固定候选内审7明确通过。
- SSR首跑5项失败因测试断言误匹配转义文本/快捷动作标签；已改为实际属性/状态元素定位，原失败逐字节gzip及哈希留在evidence/sidebar-first-test-failure.*。没有将其改记为首跑通过。
- 本批完整check已exit0：20个TS测试文件706项、Python1052项，lint/format/typecheck/build/ruff通过；证据见evidence/verification-3a4c2ea.json。该组件尚未在App挂载，SSR不等于浏览器交互/真实页面/可访问性视觉或Electron验收；后续仅在获批T00/I06/T01接口及隔离环境接线验证。
- 原第九节及无桌面约束已由总控消息实际透传、全文读取并核对共同指令SHA9717f699…；详见policy-receipt-2026-10-21.md。未重建Goal、未改冻结输入，纯政策补充不单触发产品重审，本批实际新代码已另行验证/内审。无额度告警/消费或GUI操作。
