# T06 UI 完整独立只读审查

结论：不通过。发现 3 项可复现 P2；21 项既有单测和正常 headless 交互通过，不能覆盖这些负例。

来源：父 agent /root 的新独立审查派发。审查者 /root/behavior_independent_review。唯一工作树 /Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior-ui；分支 feature/T06-behavior-ui；base 5f910b52c69d86a1076b2032e5d3c63e715947f3；固定 HEAD 571b4d64120c8420d527f9fda2a3cb81bbd47d3f。开始与结束身份相同，仅保护 AGENTS 未暂存。

已全文读实际 AGENTS（SHA-256 78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759）与共同指令（df09014af4d6cf757ca0977a995497f3646cd330e8921710876663a40a8cbcb4），包括原九节、无桌面与最新权限政策；完全访问不改变本次只读职责。完整 gitdiff 为 10 个授权新增文件，无共享文件改动。已读全部 10 文件，核对 FR-600–604、C/D/E.1/G.3。S1、子树以外实现与未来接线不属于受审产品。

## P2-1：无法显式表达无额外条件的行为

位置：apps/desktop/src/renderer/src/behavior/model.ts:12–23、52；BehaviorWorkspace.tsx:619–622。

条件类型只有 equals/exists/type，而 conditions 强制 min(1)。以 PRD G-behavior 的 X 为例，无额外条件、触发后写 T1.P=true 的草稿，validateDraft 返回 conditions 结构错误。编辑器没有 always/无额外条件的明确选项，用户只能添加改变语义的条件才能提交。B-a/B-b 等基线同类。

影响：FR-600/G.3 所需行为无法在这个独立编辑器忠实表达。不是要求直接采用 S1 类型；而是私有编辑器本身缺少明确的无条件表达。

建议：增加显式 always/无额外条件选项，同时仍拒绝真正缺失的条件字段/未作选择，不把空输入静默解释为通过。补 author→validate→callback 的完整回归，确认无需伪造对象条件。

## P2-2：结果内部证据状态与运行状态不一致仍被接收展示

位置：model.ts:152–158；controller.ts:185–196；presentation.ts:27–40。

resultSchema 只核顶层 state/committed/error，没有核 action/notification 状态组合。构造相同绑定、state=candidate、committed=false，但 actions[0].state=applied、notifications[0].state=recorded，safeParse 成功。经真实 BehaviorController.run 接收后，展示标题“候选计划·尚未提交”，同时动作“已执行”、通知“隔离记录”。

影响：未提交候选可展示实际执行/记录证据，破坏候选与已提交结果的区分。相同缺口也适用于失败或取消响应中的矛盾条目；不能依赖未来多轮历史解释本次单 sample 的 applied。

建议：明确单次 sample 各运行状态与动作/通知的合法组合，并在严格 schema 中拒绝矛盾响应；至少候选不能带 applied/recorded。为 candidate、completed、failed、cancelled 分别加入完整正/负组合测试，保留刷新时最后一次有效结果。

## P2-3：事件载荷保留键被静默丢弃，输入内容身份折叠

位置：model.ts:253–256、275。

实际 parseEvents 对同 E1 的两份载荷 {"__proto__":"first"} 与 {"__proto__":"second"} 均返回 payload={} 且 issues=[]。Zod record 清掉该自有键，页面却报告通过并向 callback 发送修改后的内容。

影响：用户显式不同的事件内容在送执行服务之前被折叠为相同输入，影响事件内容保真和同 ID 改内容的幂等冲突检查。此项是静默丢值，不是原型污染利用。

建议：显式拒绝该类保留键并给出本地问题，或用安全自有属性表示无损保存；不得静默删除。补含保留键的精确正/负例，核对同 ID 两个不同载荷不能都成功折叠为同一请求。

## 独立验证

- npx vitest run tests/unit/t06-behavior-ui.test.ts：21 passed。
- 真实 Chrome Headless Shell：从原 verify-headless.mjs 创建临时副本，仅把组件路径改为当前固定源码绝对路径、产物目录改至系统临时目录；未改产品脚本，未覆盖原 evidence 或截图。正常键盘 Tab、缺能力禁用、事件事实编辑、候选/失败/取消/历史、刷新保留草稿与宿主回调、取消后迟到拒绝、项目切换和 1440/390 无横向溢出均通过，无 pageerror。
- 独立 artifact：/var/folders/7y/9bfdsf6j5ys67hh4tpt11k_r0000gn/T/t06-ui-review-C90L00/output/；已用 view_image 查看 width-1440.png 与 viewport-390.png。
- node /tmp/T06-UI-571b4d6-negative-probes.mjs：3 项缺陷全部复现，脚本仅在内存构建当前 model/controller/presentation，不写源文件。
- verification.json 的 7 个产品/测试/脚本哈希及 11 个原始日志/截图/artifact 哈希独立全部匹配。原 fullcheck 日志支持 651 TS/1052 Python 通过，但本审查没有重跑全仓检查，不将其冒称独立执行。
- git diff --check base HEAD 通过；最终 HEAD 不变，仅 AGENTS dirty。

两次初始内存负例工具装配失败（Vite virtual entry 路径、build 返回数组形态）原输出保留在聊天，调整仅审查工具后成功；未修改产品或既有测试以掩盖失败。

## 其余范围及未验门

完整 metadata、单组 AND、四动作字段与重排、唯一 ID/单多值拒绝与已有引用检查、显式 add/remove/set 变更和重投保留事件 ID 已核对。结果严格拒未知字段和原始 evidence；异常文本未直接回显；React 文本展示 HTML-like 通知不执行。request/project/input/behavior/scope 的迟到拒绝、取消确认前不假报取消、完成赢得竞态、刷新同 runId 与保存草稿、切项目清结果正常。UI 没有重做领域算法，没有注册公共能力或调用 window.ontolearn。

本轮只评审未接入 App 的可装配组件，exists/type/单 draft 等私有 callback 不能当已批准 S1 兼容。真实公共边界、权限与隔离来源、引擎推理/幂等/竞争、Store 事务与回滚/取消/持久恢复、真实 G.3、Agent、App 导航、Electron/macOS/Windows、包内验证、指定双模型审查、CI/push/PR/merge/发布均未验证。无 GUI/CUA/Electron/e2e/native/HMR、无凭据/支付/API操作，未改源码/配置/测试/共享报告或其他工作树。本次只写系统临时审查工具、报告和 headless 产物。
