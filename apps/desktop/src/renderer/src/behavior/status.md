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

## 指定外审后最小修复候选（2026-10-22）

已全文读取 da37709 同版两份完整指定外审：ZCode 报告 24568 bytes，SHA256 `b7715b6dd4d8b4caadfdeebc59136923e610ff1280590b63f4a0e04010061cfd`；MiniMax 报告 45074 bytes，SHA256 `929a20820b916c60d4ade7f57195f8db7a59c63359bccd9ea13e76d13b2c2a26`。原文位于两独立 review worktree 的 `docs/reviews/T06/ui-round-1/`，父任务封存最终原件与 raw 后才授权本树编辑。Z 未提出新 P1/P2；MM 新 callback 引用变化 P2 必须实修，不以宿主 useMemo 或条件通过措辞关闭。未读取 S1 当前意见。

产品已固定为 `97074205d677a8cc272426b1bcabe7140b5be085`。请求生命周期 token 与显示 epoch 分离，同 context callback 引用变化只更新未来调用；真实 Promise 未收尾前保持禁用并防重入。切换真实上下文或 invalidate 拒绝旧结果，切回仍在途的输入继续等待；旧 Promise 最后收尾不清后继 pending/cancelling。只有匹配绑定的真实取消终态可释放对应调用，不加入超时释放或持久队列。补实际 deferred/异常/四维上下文切换/切回/刷新/取消竞态/错配五字段等19例，本线共53项。

同时处理三项 P3 与请求建立边界：含保留键的混合载荷明确整事件未执行、普通字段也未提交，保留原文且不 strip；取消错配专用提示保留实际在途；UUID/请求建立失败在调用前安全返回。README 明确自由文本必须由批准 adapter 作展示白名单映射，schema 本身不证明内容脱敏，不新增猜测路径过滤。index-key 焦点观察保留，不扩大本轮 UX 范围。

实际验证：原配置原命令 `npm run check` 本轮首轮 exit0，lint、格式、strict 类型、683 TS（本线53）、构建、ruff、1052 Python 完整通过。日志 `test-results/t06-ui-r3-check-first.log`。最初专项 lint exit1 是新增 mock 声明16处未使用形参，已改为带泛型的 vi.fn；没有改 lint/format 忽略。`t06-ui-r3-target-lint-first.log` 明确标为工具 session 4613 原输出的忠实转录，不能当 shell tee 原件。首专项单测日志 `t06-ui-r3-unit-first.log` 为实际53通过。

Headless 首轮 exit1：第一次本地检查滚动等待 element stable 超时，原日志 `t06-ui-r3-headless-first.log`、`t06-behavior-ui-r3-1792665050352/failure.txt` 与可访问树保留；best-effort failure.png 未生成，不声称有失败截图。尚无唯一根因，不预断环境抖动或已根治。第二完整脚本 exit0 且无键盘备选；最终加入诊断后的完整脚本 exit0，输出在 `test-results/t06-behavior-ui-r3-1792665372841/`，日志 `t06-ui-r3-headless-final.log`。三次本地检查均记录唯一 locator、box、字体 loaded、无 transform/animation 及滚动前后位置，并实际鼠标点击成功，`interactionFallbacks=[]`。脚本只对无写副作用本地检查允许超时后的单次 Space，保留原失败与实际模态；执行/取消不重试、不 force，不据键盘备选认定鼠标通过。本轮实际没有使用此备选。

最终完整夹具每次 render 都新建 callbacks，并通过可控真实 Promise 验证正常/异常收尾、防重入、切换/切回、错配取消、真实取消后旧 Promise 最后返回、后继取消仍在途；原 always 编辑、空条件拒绝、状态矩阵拒绝、草稿隔离、全部触发理由/动作/Diff/通知、混合载荷原文与修正后普通字段送达、1440/390 无溢出等12项链路均通过。已实际 view_image 看新宽屏与手机视口截图；不将夹具当真实引擎证据。

本树隔离安装官方 Headless Shell：ZIP 103778487 bytes，SHA256 `94e4337b70cbc5638f0935fbc46b9f242bc7416f657e3fbe924baf348404b53d`；校验并复制16个安全 regular 成员到 `out/t06-ui-r3-browser/`，逐成员回读字节/SHA，安装回执在其 `install-receipt.json`。实际版本 `Google Chrome for Testing 156.0.8078.4`；未用共享可变 cache，1248 仅为本轮工具来源，不添加为产品额外硬门。没有 GUI、Electron/native、HMR 或自动启动产物。

当前 AGENTS 已全文读回 SHA256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，保持 dirty/未暂存。旧静默桌面要求已撤回，本线遵守总控 T01 当前占用 GUI 的协调安排；不把旧禁止永久化。原571不通过、da37709独立通过、全部外审与首败仍保留；本轮重新验证源于产品修复。

七源码及 README manifest、base→固定产品完整10文件 diff 与其 SHA，以及20份新日志/图/诊断/安装回执的大小和SHA记录在 verification.json。9份 r2 原证据已逐项回读未变，旧 verification 的 Git来源和SHA保留。当前只收尾 status.md/verification.json 两份证据，产品相对9707420零diff；不修改或暂存 AGENTS、共享入口、主T06树、两外审树或锁文件。

下一可验交付是新固定产品的全范围独立审查及两指定模型新同版完整外审，旧通过不沿用。真实 App/bridge/引擎/Store/推理/Agent/G.3、原生平台/包内、CI、推送、PR、合并和发布均未据本轮关闭。
