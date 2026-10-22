# T06 UI 外审处置与最小修复设计（静态准备）

2026-10-22。当前仅静态准备，不代表修复、验证或新候选已完成。原件 raw 封存完成与可编辑回执尚待父 agent；在此之前不改冻结 UI、测试、脚本、README、status 或 verification，不运行新测试。未读取 S1 当前任何意见。

## 输入与身份

- 唯一开发树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior-ui`，分支 `feature/T06-behavior-ui`；base `5f910b52c69d86a1076b2032e5d3c63e715947f3`，产品 `da37709dcf09e04ded767ab2d08c26bbd8df24f3`，当前流程 HEAD `3b3af941c73b7a5d416fda50ec6fb8102992551f`。实际状态仅保护 AGENTS 未暂存。
- 已全文读当前 AGENTS，SHA256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，以及根 `iteration-control/2026-10-21-weekly-release/desktop-operation-policy-20261022.md`：原静默限制已撤回；当前互斥桌面资源归 T01，本文不使用 GUI/native。旧 no-GUI 记录按历史时点保留，不作为永久产品门。
- 已全文读自身 ZCode 报告：`.worktrees/T06-ui-zcode-review-da37709/docs/reviews/T06/ui-round-1/zcode-glm53.md`，24568 B，SHA256 `b7715b6dd4d8b4caadfdeebc59136923e610ff1280590b63f4a0e04010061cfd`。
- 已全文读自身 MiniMax 报告：`.worktrees/T06-ui-minimax-review-da37709/docs/reviews/T06/ui-round-1/minimax-m31flash.md`，45074 B，SHA256 `929a20820b916c60d4ade7f57195f8db7a59c63359bccd9ea13e76d13b2c2a26`。报告虽对阶段给条件通过，但新 P2 按父 agent 指令实际修复，不能以宿主 useMemo 约束替代关闭。
- 已回读当前全部 UI 源码/脚本/专项测试及 README；PRD FR-600–604、D.1/D.2、E.1、G.3 对应条款。原 571 三 P2 的关闭及 da37709 本地独立 Pass 保留历史，不被本轮新增问题抹去；新实现变化需新完整验证/独立审查/双方同版外审。
- 模型外部 task/session/权限/终态/raw 的实际读回和封存由父 agent 维护；本文件不从报告内部身份声明倒推这些事实，也不自行把报告“通过”扩大为发布通过。

## 逐项处置

| 来源                                                                                  | 处置                                            | 最小改动与关闭证据                                                                                                                                                                                                                                                                                |
| ------------------------------------------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| MM P2-新-1：同 context callback identity churn 清 pending、丢在途结果并允许第二次提交 | 必修，不以宿主稳定引用换 Pass                   | controller 区分请求生命周期 token 与结果显示世代；同 context 回调重新创建仅更新后继调用使用的函数，不等于实际输入/权限版本变化，不清除真实在途。run/refresh/finally/cancel 都按具体 operation token 管理，详见下节。真实版本/范围切换或显式 invalidate 仍拒旧结果。                               |
| MM P3-新-1：混合载荷整事件拒绝的指引不完整                                            | 补文案和混合正负例，保留正确拒绝策略            | 提示明确“该事件整体未执行，普通字段也不会提交，原文保留，请修正保留键后重试”。单测及 headless 验证混合原文保留、执行计数不增；手工修正后只送达完整普通字段。禁止自动删除保留键或提交剩余字段，不能静默改变事件内容身份。                                                                          |
| MM P3-新-2：取消回包绑定错配使用通用结果提示                                          | 修复专用提示                                    | cancelled schema 通过后，先核对原 operation 的 project/input/behavior/scope/requestId，再接收取消终态；错配保留原 pending，提示“取消未确认，原请求继续等待”，不假报取消。原 run 随后可正常收尾。                                                                                                  |
| MM P3-新-3：detail/reason/freshnessDetail 自由文本的适配器残余风险                    | 保留原边界，明确 T00 装配检查，不擅加启发式过滤 | 将这三个字段的可信来源、白名单格式化/受限参数列入装配前必过项；沿用禁止回传原始异常/evidence/堆栈/路径/凭据的声明。UI 继续固定错误码、本地说明、React 文本输出。不按斜杠、盘符或 stack 片段猜测并截断合法业务文本/IRI。此项不是 UI 自身缺陷，不声称真实适配器已实现。                             |
| MM 脚本 P3-新-4：一次点击可操作性超时                                                 | 有界增强准备与失败诊断                          | 对纯本地结构检查点击先等待 visible/enabled、scrollIntoViewIfNeeded，再正常 click；失败保存阶段、pageerror、按钮状态和实际首败日志，不能 force/跳断言。若采用一次重试，仅针对确定无写副作用的本地检查且保留首次失败；run/cancel 等操作禁止盲目重试。实际策略随新脚本验证核定，不保证消除环境抖动。 |
| Z 信息1：index key 的删除焦点体验                                                     | 本轮保留，作为后续装配 UX 项                    | 当前受控值正确且无 P1/P2；更换行身份模型会扩大本轮生命周期修复范围。保留提示，不冒称删除焦点已验或问题已关闭。                                                                                                                                                                                    |
| Z 信息2：精确可访问文案定位的维护成本                                                 | 记录、不为此替换业务测试定位                    | 文案变更应同步检查；继续按可访问名称测试，不以实现选择器/数量断言削弱验证。                                                                                                                                                                                                                       |
| Z 环境信息3 / MM check 首败：历史证据解包进入 lint/format 扫描                        | 保留 exit1，原配置/原命令重新全绿，不增加忽略   | 本次原开发树并无该污染目录。后续只处理本线自有新证据：先完整保全、逐字/hash核对并记录移动前后清单，再放到现有忽略的测试产物或冻结输入外。冻结输入/两模型审查树的原始证据由父 agent 封存后按所属责任处理，本子任务不跨树改/搬。不得修改 eslint/prettier/锁或以命令行 ignore 代原 npm run check。   |

补充观察分别处理：catalog 候选提示属后续引导 UX，填空式表单已符合 FR-600；事件事实变更的已知性/基数保留在真实 adapter 的装配验收，不重做 UI 领域引擎；`crypto.randomUUID()` 初始化异常可纳入本次请求建立的 try 内并给固定失败提示、不启动 pending/调用服务，不新增非安全 ID 降级；同 ID 事件重投仍保留事件 ID，仅新 requestId 变化。

## P2 请求生命周期方案

### 1. 两类事实分开

- **生命周期归属**：每个真实 run/refresh 有唯一私有 operation token，保存原 binding、种类、原草稿 revision、开始时的显示 epoch。token 不由新的 callback 引用、新的 React render 或错误回包重置。此信息仅是组件内在途 bookkeeping，不是第二套持久任务/Store 权威。
- **显示资格**：结果仍须匹配 operation、原绑定/requestId、refresh 原 runId、当前 project/inputVersion/behaviorVersion/scopeId 和显示 epoch，并经过现有严格结果矩阵。上下文变更或显式 invalidate 使旧操作结果不可作为当前结果展示。
- `finally` 的物理收尾只判断 token 是否仍拥有那项在途，不用“结果可显示”作为清除在途的前置；否则 epoch 已变化时会永久 pending。旧 operation 的 finally 不得按一个布尔 pending 清除后继 operation。

### 2. configure 与同 context 函数引用变化

同一个真实 context 中，新的 services 对象/箭头函数仅更新未来调用的可用函数。引用不同本身不证明业务版本、隔离快照、权限或连接世代改变；因此不调用 invalidate，不清 pending/cancelling，也不伪造“能力连接已变化”的领域失效。已开始的 run/refresh 继续等待它实际调用的 Promise，正常同绑定结果仍可接收。可用 callback 被撤下也不能把尚未收尾的调用变成“已停止”；只影响后续是否可启动或发取消请求。

真实输入/范围变更继续由 context 的真实版本和显式 invalidate 表达；不能靠引用相等冒充来源/权限证明。README 可以说明该私有语义，但不把 useMemo 作为防重入成立的前置。

### 3. 同上下文防重入与切换回来的在途

组件内按四项 context 键保存尚未真实收尾的 operation。run/refresh 启动先查当前 context 的操作：已有则不发第二次调用；view.pending 从当前 context 的操作投影。不同 context 可以按现有行为切换，但旧操作保留自身 token。切走再切回而旧调用仍在途时，同一 context 仍投影 pending，不因切换丢失防重入。

每项操作释放时仅删除它自己拥有的 context/token；只有当前 view 正在显示该 token，才更新当前 pending/cancelling。这样旧输入 Promise 最后才 resolve/reject，也不能清除新输入正在等待的后继请求。结果 epoch 失效与此释放逻辑分开，旧版本结果不回显。若该最小记录需要资源上限，只按真实宿主任务能力另行接线，不能伪造取消释放，也不新增持久队列。

### 4. 取消与最后才返回的原 Promise

取消尝试也有自己的 token，锁定它要取消的原 operation binding 与所调用 callback；引用变化不能把取消标志误归给另一项 run。ack、错误、绑定错配只结束这次取消尝试，原 operation 仍在途。只有严格匹配的真实 cancelled 终态才能释放原 operation；这时原 run Promise 可能尚未返回，但它的 token 已被关闭。

若此后用户发起新 run，新 token 独立存在。原 run 或旧 cancel Promise 迟到后的 receive/catch/finally 因不再拥有相应 token，不能显示、清 pending、清后继 cancelling 或覆盖后继 notice。完成先赢时同理拒绝迟到取消。取消 callback 的可用性仍由当前可信适配器给出，不能把捕获旧引用扩大为绕过当前授权。

### 5. 必加真实反例（在封存放行后执行）

1. deferred runA 真正在途，同 context 换为新 runB/refreshB/cancelB 引用并多次宿主重渲染；pending 保留、runB 调用次数为0，runA 同绑定正常结果可接收并正常释放。
2. 上述 runA reject：固定安全失败提示、只清自己的在途，无永挂；继任 runB 此后才能启动，原事件 ID 保持。
3. 真实 inputVersion/behaviorVersion/scope/project 切换：旧结果不显示；新操作 pending 期间旧 Promise 最后 settle，不能误清新操作。
4. 切离再切回同 context：旧操作未收尾时仍拒重复调用；已失效显示 epoch 的结果只作收尾、不变回当前结果。
5. invalidate/unmount 后旧 Promise 收尾：显示拒绝但 bookkeeping 释放，不能形成永挂 pending。
6. refresh 在途 callback churn 保留原 runId、草稿与请求，不重发事件；Promise 最后收尾只释放自己。
7. 取消在途 callback churn；取消错误/ack/绑定错配专用提示且原 run 保留；取消先完成释放后立即启动继任，新请求 pending 时原 run 最后返回不能清继任；完成先赢拒迟到 cancel。计数与精确 request/token 归属均断言。
8. 真实 headless 宿主夹具故意每次 render 构建新 callback（不 useMemo），通过状态/编辑触发重渲染；真实 deferred Promise 放行前按钮保持禁用，计数不增；放行/失败/取消后正确恢复，并继续全部既有正负例/宽度/键盘/文本安全断言。

## 放行后的交付与门禁

获得父 agent 的原件封存完成/可编辑回执后，仅在原授权 `behavior/` 和 `tests/unit/t06-*.test.ts` 修改必要实现、测试、脚本及本线证据，不写主 T06、公共 App、锁、全局控制或两模型审查树。固定新的完整 source/diff/hash，执行专项及实际 headless、原 npm run check；首失败保留，日志/截图不覆盖 r1/r2/本轮外审原件。按变化做完整独立复核，再由父 agent 预约双方全新同版完整外审，不沿用本轮报告作为新产品 Pass。

本阶段没有修改冻结实现或执行测试。下一可验交付是封存放行后的 P2/P3 最小修复候选及真实边界证据；正式接线、父 FR、原生两 OS、CI/PR/远端/发布门保持。
