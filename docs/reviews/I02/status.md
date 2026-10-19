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
