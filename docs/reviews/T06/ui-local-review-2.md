# T06 UI 修复候选完整独立只读复核

结论：通过本次未接入 App 的可装配 UI 组件完整本地复核。原 571b4d6 不通过结论保留；3 项历史 P2 均已实际关闭，未发现新的实质缺陷。本结论不是指定外审、真实领域集成或父模块验收通过。

## 来源、身份与规则

来源：父 agent /root 新派发的完整独立审查；审查者 /root/behavior_independent_review。

- 唯一工作树：/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior-ui。
- 分支：feature/T06-behavior-ui。
- base：5f910b52c69d86a1076b2032e5d3c63e715947f3。
- 固定受审 HEAD：da37709dcf09e04ded767ab2d08c26bbd8df24f3。
- 开始与结束均仅 AGENTS 受保护未暂存，无受审源码/测试/配置修改。
- 实际全文读取 AGENTS，SHA-256：78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759。
- 实际全文读取共同指令，SHA-256：b24c4c88404f422c5fae4bf6c01e231b678e46741250801e8100cc62a31fec39；包括原第九节、无桌面与最新默认权限政策。
- 全文读取三份已生效 I05→T01 format3、I06→T01 format3、I05→T03 build 交接：T01 共享13、T03 build4、I06其余6各自唯一维护。本任务不写这些路径，完全访问不扩大只读职责。

## 完整范围

完整 base→HEAD diff 为原授权 10 个新增文件，未含共享 App、style、bridge、Store、锁或配置。已逐一读取 BehaviorWorkspace.tsx、README.md、behavior.css、controller.ts、model.ts、presentation.ts、status.md、verification.json、verify-headless.mjs 以及 tests/unit/t06-behavior-ui.test.ts。按当前全部源码重新核对，不仅看三处修复 diff。

已读取原独立报告 /tmp/T06-UI-571b4d6-independent-review.md，并重新核对 PRD FR-600–604、附录 C/D/E.1、G-behavior/G.3 的原条款。只审查 UI 能证明的部分；没有将单 draft/exists/type 等私有组件类型当作已批准的 S1/公共适配。

## 三项历史 P2 的关闭证据

1. 无额外条件表达：conditionSchema 增加严格 always 对象，validateDraft 不要求其伪造 object/property；编辑器确有“无额外条件（恒真）”选项并隐藏无关字段。conditions 数组仍 min(1)，缺字段/空数组/always夹额外字段均拒绝。单测覆盖 X/B-a/B-b 向 runSample 送达精确 always；本次真实 headless 从编辑、宿主 onDraftChange、空组拒绝、重新选择到执行 callback 的完整路径通过。此项关闭。
2. 矛盾证据组合：resultSchema 对单次 sample 明确四种运行状态与动作/通知的矩阵；候选只允许 planned/deduplicated/skipped 和 candidate通知，完成允许 applied/deduplicated/skipped 和 recorded通知，失败/取消只允许 rolled_back/skipped 和 discarded通知。顶层 committed/error 与过期说明约束保留。新增测试遍历全部60组合，四状态 controller 负例拒绝，矛盾刷新保留上一份有效结果及草稿。本次 headless 实际重现原 candidate+applied/recorded 反例并确认拒绝，新 run 不展示该证据，刷新保留旧有效结果。此项关闭。
3. 载荷静默丢值：JSON.parse 后、z.record 前检查自有 __proto__/constructor/prototype（含转义形式）；拒绝并保留编辑原文，不进入 callback。新增测试确认两个同 ID 不同 __proto__ 内容均拒绝、三类保留键均拒绝、普通字段完整保留。本次 headless 对原两份载荷逐次点击执行，问题可见且 callback 计数不增加。此项关闭。没有将原丢值问题错误描述为原型污染利用。

## 全范围其余核对

- FR-600：名称/说明/事件/条件/动作/效果/启用/优先级/版本完整；单组 AND、唯一行为ID、编辑现有ID例外、四动作类型与顺序编辑、显式always均存在。
- FR-601/602：UI仅提供内部安全动作；单值关系追加拒绝、多值覆盖拒绝、未知对象/类/属性/IRI引用及同实例先创建后引用检查保留。真正条件快照/写入意图/竞争/资源由领域服务负责，界面未重做引擎或伪造其通过。
- E.1：事件与事实变更数组顺序保留，显式 add/remove/set 可编辑，重复运行保留原事件ID；批内重复ID和不合法JSON被拒；页面准确说明完整稳定排序及冻结条件。
- FR-603/D：条件触发/未触发理由、完整动作顺序与状态、Diff新增/撤回、通知、请求与run/断言/推导/语义版本可见；当前/过期/历史及候选/提交/失败/取消区别明确。修改草稿/事件后保留旧请求结果并提示旧依据；刷新不重发事件、不覆盖草稿，仅接受同runId。
- 请求与异步：项目/inputVersion/behaviorVersion/scope/requestId绑定和epoch拒绝迟到结果；切项目/输入上下文清结果，按约定保留同项目草稿；能力连接变化和卸载后回包无覆盖。取消必须收尾终态，ack不冒充取消；取消先赢拒后完成，完成先赢不被取消错误覆盖。
- 安全与能力边界：服务缺省为空时执行禁用；result严格拒未知字段/evidence，异常文本不直接回显。React正常文本展示HTML-like通知，无生成img或执行内容。没有调用 window.ontolearn、注册公共能力或保存正式数据。
- 视觉与键盘：实际 Tab 焦点、控件可访问角色、1440/390无横向溢出通过；已查看本次宽屏与手机视口截图，always显示及分栏/窄屏布局正常。

## 本次独立实际命令与产物

1. npx vitest run tests/unit/t06-behavior-ui.test.ts：34 passed，退出0。
2. 从当前 verify-headless.mjs 创建临时副本，仅将 component 指向当前固定源码、output 改到临时目录；复用本树已安装 Headless Shell。真实 headless 全链路退出0，包括三项反例关闭、键盘、正常状态、刷新、取消竞态、项目切换及1440/390检查。没有覆盖原 r1/r2 产物、没有Vite HMR或Electron。
3. 独立临时目录：/tmp/t06-ui-da37709-review-6R9rwE/；脚本 verify.mjs，原日志 headless.log，output/evidence.json、width-1440.png、width-390.png、viewport-390.png及临时构建产物。已用 view_image 查看本次 width-1440.png 和 viewport-390.png。
4. 独立重算 verification.json：7个当前产品/测试/脚本SHA、9个r2日志/产物SHA全部匹配。从571固定Git对象读取旧verification，旧manifest SHA匹配，11项原日志/截图/artifact全部未变；旧独立报告和负例工具SHA亦匹配。
5. git diff --check base HEAD：通过。最终HEAD及dirty重新核验。

原 fullcheck 664TS（本线34）/1052Python 的原日志属于开发线执行，本次以源码/产物hash和日志核验其对应关系；依指令未无必要重跑全仓，不能称独立执行全仓。旧571的651TS/21专项记录仅为历史，不抵新候选。

## 未验门与操作边界

未接入 App/公共 bridge/受信生命周期与权限；未做真实引擎、Store原子提交/回滚/取消/恢复、推理、幂等/竞争领域执行、Agent、真实G.3完整基线、原生Electron/macOS/Windows、正式包内验证、指定GLM-5.3/M3.1-Flash外审、CI/push/PR/merge/发布。私有回调和开发夹具不是这些门的证据，父FR和完整发布仍未关闭。

本次没有GUI/CUA/Electron/e2e/native/HMR/Keychain/凭据/付费/模型API操作，不修改任一受审源码/测试/配置/报告、其他树或总控文件；只写/tmp审查脚本、构建/截图/日志及本文。默认完全访问/始终授权政策没有被解释为修改或绕过门禁的授权。
