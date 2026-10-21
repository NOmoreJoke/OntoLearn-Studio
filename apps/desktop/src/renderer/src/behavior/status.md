# T06 行为 UI 子任务回执

2026-10-21，独立子任务，沿用父 T06 Goal。没有建立第二个 Goal。以下启动与首次验证保留为 `571b4d6` 历史；最新修复另见末段。

- 工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior-ui`。
- 分支：`feature/T06-behavior-ui`；实际启动 HEAD/base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 启动时仅受保护 AGENTS 未暂存，SHA256 `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`；已全文读 AGENTS、共同指令、frontend-design、FR600–604/C/D/E.1/G.0/G.3。
- 共同指令启动 SHA256 `9717f699e14b5941e15d90269f33cbebc32ef9bec6e7439739be848753419880`；已接收第九节、无桌面全文。
- 总控授权补充后实际读回 AGENTS SHA256 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`、共同指令 SHA256 `df09014af4d6cf757ca0977a995497f3646cd330e8921710876663a40a8cbcb4`；已读完整 external-review-permissions。该政策不改变 UI 禁止 GUI/审查应用的任务约束，不改写受审服务或重启 Goal。
- 责任仅新增 `apps/desktop/src/renderer/src/behavior/` 与 `tests/unit/t06-*.test.ts`。AGENTS 保持未暂存；没有修改共享 App、style、bridge、Store、主树、依赖锁、CI 或总控文件。

已实现可装配草稿、单组条件、四类安全动作及排序、显式事件/断言变更、缺省能力禁用、受限结果解析、完整触发原因/动作轨迹/Diff/通知及失败/取消/过期/历史展示。条件评估及排序文字遵守 E.1；没有在 UI 重做行为引擎。

实际执行：`npm ci --ignore-scripts`、`uv sync --frozen` 成功。最终 `npm run check` 完整通过：lint、格式、strict 类型、651 项 TS（本线 21 项）、桌面构建、ruff、1052 项 Python；源码为独立批准基线，没有采用 S1 引擎实现。补入单值关系追加拒绝、单值 IRI 覆盖与多值追加的明确正/负例。

Headless 已实际通过：未接入服务禁用、键盘 Tab、事件/事实变更、候选与失败/取消/历史、触发理由/完整动作文本/通知安全、刷新保留草稿及宿主回调、取消迟到完成拒绝、项目切换、1440/390 无横向溢出。已用 view_image 实际检查宽屏、手机全页与手机视口截图。所有输出均为明确标识的开发夹具，不是引擎或生产结果。

首败保留：初始 Vite 虚拟 entry 解析与缺少 Headless Shell 的工具原输出在本会话；后续嵌套 select 精确 label 定位超时有 `test-results/t06-ui-headless.log`、`t06-ui-headless-2.log` 原始日志，并实际读可访问树后修正为 role 定位。首次全 check 在开发中脚本格式未定时失败，保留 `test-results/t06-ui-check.log`。修复后的完整通过与最终通过分别保留 `t06-ui-check-2.log`、`t06-ui-check-final.log`，最终 headless 日志为 `t06-ui-headless-final.log`。均为本树忽略产物，不混入源码。精确源哈希、日志/截图哈希与验收边界见 [verification.json](./verification.json)。

下一可验交付：本地可恢复提交交父 agent 完整独立内审；抽查反馈不作为独立通过。未作指定外审、推送、PR 或合并。正式 App 接线、真实引擎/事务/Agent 联验、原生窗口和首发平台验收仍由父模块按原门禁完成。

## 独立复核修复（571b4d6 之后）

完整独立复核终态不通过，3 项 P2；原报告 `/tmp/T06-UI-571b4d6-independent-review.md` 与负例 `/tmp/T06-UI-571b4d6-negative-probes.mjs` 保留。原候选提交、首败工具原输出、原始日志和 `test-results/t06-behavior-ui/` 截图均保留；新 headless 输出改用 `test-results/t06-behavior-ui-r2/`，不覆盖原件。

本轮只修三项：显式 always 且空/缺条件仍拒绝；单轮运行/动作/通知状态矩阵拒绝矛盾；JSON 解析后、record 归一化前显式拒绝三类保留键，普通内容无损。没有将保留键丢值描述成原型污染利用。新增真实反例覆盖全部 60 个状态组合、controller 的拒绝/刷新保留、无条件草稿与 callback、同事件两个不同保留键内容均不送达。初次新增单测 34 项通过；最终完整 `npm run check` 通过 664 项 TS（本线34）、1052 项 Python及 lint/格式/strict 类型/构建/ruff。新 headless 完整反例与正常链路通过，已实际 view_image 检查新宽屏/手机截图。新 source manifest 的7项源哈希与最终验证一致；此前11项原始日志/截图/artifact逐项复核未变。

已在安全边界全文读最新共同指令 SHA256 `b24c4c88404f422c5fae4bf6c01e231b678e46741250801e8100cc62a31fec39`，保留原 `df090...` 历史输入；三份已生效 handoff 的 SHA256 分别为 `18485767098d448a4fcce2fc7e59b5a325433826894b98111cab96926fdc2097`（I05→T01 Python4）、`add9884ab9a0cda3a8a562f26a3b7c515255919d65eb0487d6c254681ed4991d`（I06→T01 canonical/main8）、`88057b59e173453d197bfeae183dc99b8c09c71e30d518781bf774ebc037e95b`（I05→T03 build4）。AGENTS 仍 `78df...a759`；T01 共享13、T03 build4、I06 剩余6各自维护，本线只改原10独占路径，不采用未批准实现。本轮重验来自实际 UI 改动，不来自纯政策更新。

r2 首败是验证脚本用精确 label 匹配已有内容的 textarea 超时，保留 `test-results/t06-ui-r2-headless-first.log`，修正为 textbox 可访问角色后，最终 headless 在 `t06-ui-r2-headless-final.log` 完整通过。原始完整 check、脚本定位修正后的最终完整 check 分别保留 `t06-ui-r2-check-first.log`、`t06-ui-r2-check-final.log`。新 JSON 明确保留原571版本的 verification Git对象/hash，并分别记录历史与当前证据。

本地修复与验证完成，下一步为新固定提交的完整独立复核；没有自行将原不通过改为独立通过。尚未推送/PR/合并，正式接线及父模块/发布验收边界不变。

## da37709 完整独立复核终态

父 agent `/root` 新派发 `/root/behavior_independent_review` 对 base `5f910b52c69d86a1076b2032e5d3c63e715947f3` → 产品 HEAD `da37709dcf09e04ded767ab2d08c26bbd8df24f3` 的全部10文件只读复核，已实际终态通过，开发线已全文读回 `/tmp/T06-UI-da37709-independent-review.md`，报告 SHA256 `0ed80af74646509741dc0e7a40fb142713b0605c30dc97735b1eba8c1680c9b3`。原571完整不通过及三项问题原件继续保留。

三项均经独立实际关闭：P2-1 explicit always 无伪造对象条件、空/缺条件拒绝、宿主与执行回调保真；P2-2 60种单轮状态组合、四状态 controller 负例与刷新保留；P2-3 两份不同同ID保留键载荷均拒绝且 callback 计数不增，普通内容完整保留。独立者实际运行34项专项单测及真实 headless 全链路并退出0，复验7源/9当前证据/旧manifest及11旧产物哈希、最终HEAD和仅AGENTS dirty。开发线完整check的664 TS/1052 Python日志由独立者核对对应关系，未冒称其独立重跑全仓。

独立 headless 产物在 `/tmp/t06-ui-da37709-review-6R9rwE/`（`headless.log`、`output/evidence.json`、宽屏/手机截图）；独立者已实际看图，本线仅读取产物核验记录，不重跑无变化验证。本次只更新 status.md 与 verification.json 作为流程证据；7产品/测试/脚本及README相对受审产品da37709零diff，保护AGENTS仍未暂存。指定双模型外审、真实App/bridge/引擎/Store/推理/Agent/G.3、原生平台与包内验证、CI/推送/PR/合并/发布仍未验，不据此关闭父FR或正式接线门。
