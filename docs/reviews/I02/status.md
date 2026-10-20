# I02 / C1 状态

- 会话：01a15677-7ea3-7da1-b77b-c253d5815815；唯一功能：显式 CSP 与窗口生命周期。
- 当前阶段：实现与验证；未冻结、未提交、未 push、未创建第三方任务或 PR。
- 分支：feature/I02-csp-window-lifecycle；base：1b6df7a220fc9a67d7046133a340085f03f0a96c；head 待冻结。
- 需求：../../iterations/I01/inputs/goal-objective.md 第四节完整提示词，scope.md I02，m0-review-and-update-plan-2026-10-19.md C1；PRD V0.6 8.7/10.3/10.4/12.5。
- 已核验 origin 与 develop；已安全快进本地 develop 后新建分支。唯一冲突 I01/status.md 按 before-I02 备份恢复，64 项哈希全部一致。
- 选择生产仅 meta；开发 header 和生产 meta 均由 src/csp.ts 生成。理由与实际矩阵待记录。
- 非目标：ExecutionJob/v2/业务 UI/模型网关；只有真实 health 恢复，未来任务重连留待 I04 联验。
- 门禁：实现验证后本地提交冻结；内部只读独立审查；两指定应用新任务同版独立明确通过才 push/PR/merge。
- 未决：运行验证、内部审查、双指定模型、push/CI/merge/远端核验尚未执行。下一步补充真实验证矩阵。

## 实现/验证进度

- CSP：选择生产仅 meta，资源加载前首项注入；开发仅 header，统一 src/csp.ts 生成。meta+header 比较理由见 docs/iterations/I02/design.md。
- 窗口：securePreferences 工厂；全 contents 导航/新窗口/webview 限制；app sandbox/session 权限；保持 health 当前 sender/mainFrame/可信文档三重校验。
- 恢复：原生提示，显式恢复才重建；不调用引擎/不重放。did-finish-load 清理旧异常；退出/关闭/响应恢复保护。
- 内部独立 agent 已完成只读审查和增量复核，无阻断；两项非阻断建议均采纳关闭，见 internal-review.md。
- 开发矩阵（初版）：nonce 页面无生产 meta；CSS HMR+React Refresh 保留文档与 state；资源/外联/frame enforce 阻断且本地接收端零请求；原始 executable 无 inspector 下真实 killed/unresponsive 两次恢复和三次手动 health 成功。
- 最终修订正重新执行 check/build/e2e/package。新增 6 项恢复逻辑竞态测试与原生生命周期证据分开。
- 测试夹具初期发现 Playwright loader 默认 disable-hang-monitor；没有把其下超时当成应用失败/通过。现用 --require 测试驱动启动原始 executable，无 inspector/CDP，实际应用源码/包内 main 不变。初期诊断日志保存在仓库外 iteration-control/2026-10-19/I02-diagnostics，不作为通过证据。

## 候选冻结前最终核验

- 最终实现/验收已完成；check：14 TS + 198 Python、lint/format/type/build 全成功；verify:sources 工作区13项成功。
- 构建态 e2e 2/2、真实 macOS arm64 packaged executable e2e 2/2、开发 C1 矩阵1/1（CSS HMR+React Refresh）成功。JSON 显式记录生产 app.isPackaged=true，native inspectorClosedBeforeFaults=true、killed/unresponsive 与三窗手动health。
- 最终 native 驱动为 transient MAIN inspector bootstrap → inspector.close → 故障，渲染端从未附加CDP；前述 --require 仅为已放弃的测试夹具探索，不是最终证据。
- 全部原始矩阵/命令/打包哈希与边界见 docs/iterations/I02/acceptance.md、commands.md、evidence/。
- 内部独立 agent 的三项建议（措辞、恢复竞态、native驱动有界失败清理）均已采纳并复核关闭；不替代指定双审。
- 64项保护哈希一致；HMR两源文件git diff为空；没有修改总控state、PRD产品范围或后续功能。
- 正冻结本地候选，base固定1b6df7a220fc9a67d7046133a340085f03f0a96c。以下head将在提交后追加；实现/测试/配置/依赖/验收自该提交起冻结。
- 双指定模型任务尚未创建；没有push/PR/merge。下一步：同一开发会话通过两应用新建Round1，重新核验根路径/模型/思考设置后派发同版完整对抗审查。

## Round 1 冻结

- base：1b6df7a220fc9a67d7046133a340085f03f0a96c。
- candidate head：2cc03da82ffccc8448c7b03dc6cff87595027653，34文件。实现/测试/配置/依赖/验收冻结。
- 候选git archive独立verify:sources成功（原归档12项），工作区13项与64保护文件有明确边界。全部15个frozen-files哈希与64个保护哈希一致。
- 后续只追加流程证据；Round1两应用任务待下面实际记录，不沿用前次I01设置。

- Round1 已实际创建并启动两个全新任务（同一开发会话通过computer use完成）：
  - ZCode dev.zcode.app，I02-R1-ZCode-GLM53-20261020-0735；GLM-5.3/最高；原生Open选择器重新核验精确Git根，分支dropdown选中当前feature；发送后实际观察工作中/停止生成。
  - MiniMax Code com.minimax.agent.cn，I02-R1-MiniMax-M31Flash-20261020-0735；UI标题“审查 I02 CSP 与窗口生命周期迭代”；M3.1-Flash/xhigh；原生Select选择器重新核验精确根，新空白任务显示本地/当前feature；发送后实际执行命令/停止生成。
- 两方均完整原始审查提示词+同一固定base/head+全部I02/C1验收，不披露另一方本轮意见；只可写各自round-1报告，不允许I02_HMR临时改源探针。
- 当前双方running，未出具/未读取本轮报告；详细task source见round-1/tasks.json。15冻结项/64保护项再次一致。保持冻结，等待两任务实际结束后完整读回判断；绝不先push。

- Round1 MiniMax任务实际结束：UI共执行11分41秒，最终“审查完成—结论：通过(Pass)”，5项非阻断/0阻断，报告artifact已显示。尚待ZCode实际结束后完整读回双方报告与逐项处理；不能仅凭UI通过推送。

- 原生提示可见性补证据待办：现有自动化只捕获showMessageBox请求并stub用户选择，不能单独证明真正native sheet显示/按钮可达。待本轮两任务实际结束后，使用真实packaged executable、不替换showMessageBox，通过computer use观察/操作崩溃与无响应提示，记录截图/原生事件/选择后UI与health。此项未完成前不宣称提示实际显示验收闭环，不push。保持实现/测试/验收冻结；仅补实际运行过程证据；若需改实现则新候选双方新任务重审。

- Round1 ZCode验证临时产物偏差：其npx --prefix asar提取在仓库根生成index.html(709字节)/index.js(208字节)，超出预期/tmp位置。开发会话实际核验二者均未跟踪、均非64保护项，分别与当前renderer HTML/preload逐字节一致（SHA 27641d729b5e3de85d639191ffdb1451c2334a4c25e5d7b36f08bd03c1731cbd / c73129a6459504e5ea13830a926b01e6d2bdb61f0d2d64505d07db8c29636130），只允许清理这两个自有提取产物。不将此隐瞒为“从未出现临时文件”；实现/测试/配置/依赖/验收未改。最终门禁仍需重新核验15+64哈希。

## Round 1 完成与原生补证据

- 双任务均实际结束，完整报告读回，GLM-5.3/最高 与 M3.1-Flash/xhigh 对固定2cc03da均明确通过，0阻断。原文hash见tasks.json；逐项处理见round-1/processing.md，不改写任何外部结论。
- 真实native补证据已完成：run-2同一packaged进程PID64273、主inspector故障前关闭、showMessageBox从未替换；真实unresponsive/killed原生sheet均截图+AX，接受后两次新窗尚未检查且手动health成功，暂不恢复无第4窗。正常quit/exit0；run-1工具干扰与不确定观察原样保留。见native-dialog-probe/README.md。
- 更正原自动化证据边界：整体stub提示API，旧矩阵不单独证明native渲染；原验收未缩减，本次真实UI已补齐。M-01明确same-build vs跨构建不可复现；M-03等非阻断缺陷明确延期，未声称修复。
- 仅追加docs/reviews/I02流程证据，15冻结路径/64保护路径待最终重核；未push/PR/merge。

- 最终独立内部agent只读复核流程证据：15冻结文件匹配、实现/测试/验收diff为空；Run2原生提示/点击/同进程恢复及M01/M02/M03处理无夸大，可按原流程第五节8条关联同候选。指出driver.log被*.log忽略，已明确单文件force-add保存，避免证据断链。
- 推送前完整性：pre-push-integrity.json记15冻结/64保护0差异、双方报告hash匹配、candidate后实现diff为空；fetch origin/develop仍为base 1b6df7a，无远端feature。仅待流程证据提交，再正常push/PR/CI/merge。

- 流程证据暂存50文件，均在docs/reviews/I02；git diff --cached --check仅原始unified diff上下文的空格+tab标记告警（package-main-diff.txt），保留原文，非源码缩进缺陷；没有实现变更。
