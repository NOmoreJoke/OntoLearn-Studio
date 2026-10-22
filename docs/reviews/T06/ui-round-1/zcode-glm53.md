# T06 UI 全新独立完整只读对抗审查（ZCode GLM-5.3，ui-round-1）

日期：2026-10-22。审查者：ZCode（GLM-5.3）指定独立外审。唯一报告路径即本文件。

## 最终结论（先读）

**对"未装配独立行为工作台 UI 组件完整范围"的判定：通过（本子阶段范围内，全部指定验证完成）。**

本轮全部指定验证均实际执行并通过：专项 34 单测 exit 0；check 六子命令受审面全部通过（664 TS / 1052 Python）；**完整 headless 正反例在默认 1248 路线实际运行 exit 0**（Chrome Headless Shell 156.0.8078.4 / playwright 1.64.1，8 组检查含三项 P2 反例、取消竞态、键盘 Tab、无 pageerror、1440/390 无横向溢出与新截图实际查看）；历史三项 P2 经我独立复核确认关闭；补充对抗探针全部通过；未发现新的 P1/P2 缺陷。本判定仅覆盖未装配独立组件子阶段，不得用于关闭 FR-600–604 父模块或任何未验门（见第 7 节）。

**结论演变记录（分账）**：本报告初版结论为"无法验证"——当时 Headless Shell v1248 经 5 次官方尝试（owner 4 次 + 我方 1 次 ECONNRESET）无法获取，分发网关诊断为服务端 400。随后 owner 经 Google 官方 GCS JSON API 同 bucket/object 入口完成下载并安装到本树（我方独立复核，见 4.2），headless 验证随后实际完成，结论据实更新为"通过"。初版的失败记录与诊断全部保留于 4.2，未删除或美化；1248 只是 playwright 1.64.1 锁定的默认配套，不构成永久产品硬门（用户 2026-10-22 纠正），本轮实际使用即默认 1248 路线，无需任何 executablePath 例外。

## 1. 任务来源与身份

- 来源：owner 派发的冻结输入（原提示 20978B，SHA256 `e2d3a0e6ce84427b9cc2b5b2f31dececad34175b1ac78f51effea94786b0cc7a`，副本 `docs/reviews/T06/ui-round-1/zcode-glm53-input.md`）+ 当前独立工作区及证据映射补充，合成完整派发文件 `zcode-glm53-dispatch-20261022.md`（30774B，SHA256 `acefdd54146760a1fb6e2a378a4cb8909a191ca4d77db5a0f06cc57f6112cc18`）。
- 粘贴文本与派发文件经 `cmp` 核验**逐字节一致**，哈希与用户声明一致；派发文件第 54 行起与原输入副本逐字节一致（第 53 行为分隔线后的一个排版空行，非内容改动）。补充部分（1–50 行）声明了 [REVIEW_WORKTREE] 到本树的唯一映射，满足"没有 addendum 就停止"的前置条件。
- 模型自身可核事实：本会话由 ZCode 桌面应用运行，底层模型标识为 `account:bigmodel-individual-coding-plan/GLM-5.3`，与指定模型 ZCode GLM-5.3 相符；思考等级与任务权限模式我无法从会话内部自证，按输入要求属 owner 外部读回项（派发补充要求读回 permission.mode=yolo；本报告不以派发声明冒充已核验）。
- 真实 task/session/turn ID：模型内部不可见，须由 owner 外部读回；本报告只记录模型侧可核事实。

## 2. 工作区与来源核验（全部实际执行）

- 唯一工作区：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-zcode-review-da37709`；`git branch --show-current` 为空（detached），HEAD = `3b3af941c73b7a5d416fda50ec6fb8102992551f`（流程 HEAD），与声明一致。审查开始/结束 `git status` 相同：`M AGENTS.md`（受保护 dirty，未还原/暂存）+ 未跟踪 `docs/reviews/T06/`、`ui-review-evidence/`；产品路径零变更。
- base `5f910b52c69d86a1076b2032e5d3c63e715947f3`、产品 `da37709dcf09e04ded767ab2d08c26bbd8df24f3`、旧失败产品 `571b4d64120c8420d527f9fda2a3cb81bbd47d3f` 均实际解析存在。
- AGENTS.md SHA256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4` 与声明一致；PRD `PRD-本体学习与落地Agent工作台.md`（93584B）SHA256 `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb` 与声明一致。
- `git diff --binary base 产品` 实际生成 124657B，SHA256 `0b2ebc607543cfbc0a02a2856c1fddbf4b4a92c6204cf186f3655d0b90f8a2b4` **匹配**；10 文件全部为新增（2840 insertions，无删除、无共享文件改动）。已读完整 diff（全新增即完整内容，并与下述逐文件全文阅读互相印证）。
- 产品→流程 HEAD 差异**仅** `behavior/status.md` 与 `behavior/verification.json` 两文件（+42/−3），已读完整 patch，与"产品之后仅流程变化"一致。注意 verification.json 新增段声称三项 P2 已由 `/root/behavior_independent_review` 关闭——该声明是我本轮必须自行重核的对象，见第 5 节。
- 7 源码/测试/脚本三方 SHA（工作树 vs Git 产品 vs 流程 HEAD）**全部一致**且与派发基准一致：BehaviorWorkspace.tsx `0e7012e1…`、controller.ts `36d59ea1…`、model.ts `b246491a…`、presentation.ts `5966010c…`、behavior.css `869ebea1…`、verify-headless.mjs `a4573ccc…`、t06-behavior-ui.test.ts `cad7082f…`。
- 旧失败产品 `571b4d6` 的 verification.json Git 对象实际读取，SHA256 `ddd1bc99026c51d444755ad2363423f428d84a57f2a7092b4bd42e20a3d18bc9` 与 provenance 记录一致；571→产品 delta 为 7 文件（controller.ts 无改动），三处修复点与历史报告声称一致，无其他源码夹带。
- `dispatch-preflight.json`（33417B）已读：含双模型输入元数据、来源核验、42 成员清单、owner 六项派发前提与"notExecuted"声明。其中 MiniMax 输入仅有哈希元数据，其内容我未读取。

## 3. 完整读取范围

- 受审 10 文件**全文**逐行读取（BehaviorWorkspace.tsx 804 行、t06-behavior-ui.test.ts 679 行、verify-headless.mjs 265 行、model.ts 348 行、controller.ts 253 行、behavior.css 301 行、presentation.ts 42 行、README.md 43 行、status.md 与 verification.json 当前流程版本全文）。
- PRD 原条款全文读取：FR-600–604；附录 C（能力矩阵）、D（结果状态与失效表）、E.1（事件/条件快照/写入/排序/竞争）、E.2（固定轮次状态机）；G.0（G-base/G-behavior 基线与重置契约）、G.3（B-01～B-11）、G.5（A-01～A-10）；附录 F（Agent 授权与修改表）；第 10.4/10.5 节（安全与可测试性）与第 12 章（端到端验收）。未以提示或历史摘要替代原条款。
- 历史 7 文档（本树只读副本）全文读取，SHA 全部匹配：ui-integration-handoff.md `b0403445…`、ui-local-review-1.md（571 不通过报告）`628f2370…`、ui-local-review-2.md（da37709 内部独立复核通过报告）`0ed80af7…`、ui-validation-da37709.json `a7cfcdb0…`、ui-archive-index-20261021.json `a2131587…`、ui-archive-20261021.md `33c33705…`、ui-571b4d6-negative-probes.mjs `dc8b5495…`。
- 两归档逐字节核验：`ui-original-artifacts-20261021.tar.gz`（2232198B，`a51bfec8…`）与 `ui-session-tool-records-20261021.tar.gz`（6698B，`06d2e863…`）哈希匹配；包内 manifest.json SHA 分别为 `42950c37…`/`b35e8ae0…` 匹配；成员 34+8=42、无绝对路径/`..`/链接等非 regular 条目；33 条 entries 的 bytes/SHA 全部匹配（manifest.json 自含不计）；工具记录包 6 条 call/output 记录的 `source_length_bytes_including_newline` 与 SHA 全部匹配（call_id 与 preflight sourceMap 一致：`call_5f52…`/`call_1c6b…`/`call_7aa2…`）；安全解包目录与归档成员逐字节一致、无多余文件。**未执行归档内任何代码**（preview.js/index.html/旧脚本仅哈希与只读查看）。
- 历史截图只读查看：r2 `width-1440.png`（哈希已核验的历史证据）经视觉核看，布局两栏完整、中文清晰、HTML-like 通知 `<img src=x onerror=alert(1)>` 以纯文本显示、无破损——属背景核对，**不是本轮新证据**（本轮无新截图，见 4.3）。
- 未读取：S1 当前外审的任何提示/报告/输出、另一模型（MiniMax）输入/会话/意见、任何全会话或凭据。

## 4. 本轮实际命令与结果（cwd 一律为本工作区根）

### 4.1 单测与 check

| 命令 | 结果 | 首败/限制 |
| --- | --- | --- |
| `npx vitest run tests/unit/t06-behavior-ui.test.ts` | **34/34 通过，exit 0** | 无（vitest-unit.log，SHA `43a62f93…`） |
| `npm run check`（原样） | **exit 1，首败于 lint 阶段**：1055 个 eslint 错误**全部**来自 `ui-review-evidence/ui-original-artifacts-20261021/` 下两个历史证据解包文件（`independent-build/output/preview.js` 808KB 历史构建产物 + `independent-build/verify.mjs` 1 处未用变量）；受审 10 文件与仓库跟踪文件 **0 错误**。format:check 的 8 个警告同样全部位于证据目录。 | 这是审查树静态准备（证据解包目录未被忽略）造成的检查环境污染，**不是受审产品缺陷**；原开发树无此目录故历史 check 通过。不修改任何仓库配置，按下述分项等效重跑。 |
| `npx eslint . --max-warnings 0 --ignore-pattern 'ui-review-evidence/**'` | exit 0 | 仅命令行排除证据目录，零配置改动 |
| `npm run format:check`（原样日志分析） | 受审/仓库跟踪文件 0 警告；仅证据目录 8 个历史文件不合格 | 同上污染来源 |
| `npm run typecheck` | exit 0（两套 tsconfig strict） | 无 |
| `npm test`（全量 vitest） | **664/664 通过（16 文件），exit 0** | 与历史 664 TS 声明一致 |
| `npm run build` | exit 0（119 modules，865KB bundle） | 无 |
| `npm run engine:check`（ruff + pytest） | **1052/1052 通过，exit 0** | 与历史 1052 Python 一致 |

结论：check 的六个组成部分中，五个原样通过；唯一失败的 lint/format 仅因证据解包文件进入扫描面。**受审源码/测试/脚本在全部六项上零问题**。check 分账日志与全部产物 SHA 见第 8 节。

### 4.2 Headless Shell 1248（获取失败记录 → 官方 GCS 恢复 → 默认路线完整验证通过）

**获取失败阶段（全部保留）**：

- 事实基线：`@playwright/test` 1.64.1，`browsers.json` 要求 chromium / chromium-headless-shell **revision 1248**；本树固定目录 `out/t06-ui-review-browser` 起初仅有空 `.links`，无 1248。
- 第 5 次官方安装（owner 四次失败后）：`PLAYWRIGHT_BROWSERS_PATH=$PWD/out/t06-ui-review-browser npx playwright install chromium --only-shell` 实际执行，**exit 1，ECONNRESET**（browser-install-attempt5.log，SHA `cb35e882…`）。
- 当时的网络诊断：直连与代理对 `cdn.playwright.dev` 均 307 重定向至 `playwright.download.prss.microsoft.com`，终点对 v1248 返回 400 GatewayExceptionResponse（`X-DSGatewayServiceAPI-ErrorCode: 20012`，代理/`--noproxy` 直连相同）；旧 `storage.googleapis.com` 虚拟主机路径 owner 记录 TLS 失败。未降 TLS、未改全局网络、未用旧缓存替代。

**owner 官方 GCS 恢复（我只读核验，未冒称自己下载）**：

- owner 经 Google 官方 GCS JSON API 同 bucket/object 入口（`www.googleapis.com/storage/v1/b/chrome-for-testing-public/o/156.0.8078.4%2Fmac-arm64%2Fchrome-headless-shell-mac-arm64.zip?alt=media`）实际 TLS 200 下载 103778487B，ZIP SHA-256 `94e4337b70cbc5638f0935fbc46b9f242bc7416f657e3fbe924baf348404b53d`，MD5 与官方 `x-goog-hash` 一致，16 成员 CRC 全过；安全解包安装到本树 `out/t06-ui-review-browser/chromium_headless_shell-1248/`（原子重命名，主 binary mode 0o755）。记录见本体根 `outputs/20261022_t06_external_review/ui-browser-resolution/`（findings.md、source-and-network-findings.json、owner-install-receipt.json，均我只读）。无未知镜像、无 TLS 放宽、无全局网络改动。
- 我方独立复核：主 binary SHA256 `77d8278b1ac9d0687fad4e817ea83023ede09b1deef36e1864b49ba194ac9634` 与 owner 回执一致；`--version` 实际 exit 0 输出 `Google Chrome for Testing 156.0.8078.4`；安装目录 16 文件齐全。注：官方安装器形态的 `INSTALLATION_COMPLETE` marker 缺席（owner 以安全解包+原子重命名安装），实测 playwright 1.64 launch 按路径解析不受影响。

**默认 1248 路线完整验证（本轮实际执行，exit 0）**：

- 先以最小探针确认 `PLAYWRIGHT_BROWSERS_PATH=$PWD/out/t06-ui-review-browser` 下 `chromium.launch({headless:true})` 成功（无需 executablePath 例外，未使用任何降级路线）。
- 制作 verify-headless.mjs 重定位副本 `test-results/t06-ui-zcode-glm53-logs/verify-headless-zcode-glm53.mjs`（SHA256 `31912868…8967`）：仅两行差异——component 重定位到本树固定源码绝对路径、output 重定位到新唯一目录 `test-results/t06-behavior-ui-zcode-glm53-r3`；diff 记录于 verify-headless-copy.diff（SHA256 `30c55866…52ef`），fixture/断言/1440/390/键盘/pageerror/截图/安全设置逐字保留，未改冻结 7 源码/锁/原输入，未覆盖任何历史 r1/r2 输出。
- 运行命令：`PLAYWRIGHT_BROWSERS_PATH=$PWD/out/t06-ui-review-browser node test-results/t06-ui-zcode-glm53-logs/verify-headless-zcode-glm53.mjs`（cwd 本树根）→ **exit 0**，完整日志 r3-headless.log（SHA256 `2d566b6f…d65`）。8 组检查全部通过：未接入服务禁用+本地检查边界；显式 always 无伪造字段且回调保真+空条件拒绝；候选不冒充提交+完整触发/动作/通知文本安全+刷新保留草稿；矛盾 candidate+applied/recorded 被拒+刷新保留上次有效结果；同事件两份不同 `__proto__` 载荷显示问题且不调用执行；失败/已取消/历史分别展示；取消入口等待真实确认+拒绝迟到完成覆盖取消；1440/390 无横向溢出+切项目清除旧结果+无 pageerror。
- 新产物：`evidence.json`（SHA256 `d7397917…0b56`，与历史 r2/独立复核产物逐字节一致——同脚本同断言的预期一致性）；截图 `width-1440.png`（345183B，`da427422…b04`）、`width-390.png`（326645B，`8dcbe971…4a6`）、`viewport-390.png`（53964B，`570922bd…d30`）。
- **新截图实际查看**（本轮亲自核看，非沿用历史）：宽屏 1440 全页——夹具标记与按钮排、"运行已取消 · 本轮未提交 / 当前输入"取消终态、双栏卡片布局完整无重叠/溢出、`<img src=x onerror=alert(1)>` 通知以纯文本显示（React 文本安全实际确认）、中文清晰；手机视口 390——单列排布、卡片无破损、长 UUID 经 overflow-wrap 正确断行、中文可读。局限说明：截图为开发验证夹具（明确标注"非引擎结果 · 不接入产品"），证明组件状态机与渲染行为，不证明真实引擎、正式接线或生产数据路径；截图为静态画面，键盘路径由脚本 Tab 断言与 pageerror 计数为准。

### 4.3 补充只读内存反例探针（授权范围内，覆盖单测之外的我方对抗疑点）

`test-results/t06-ui-zcode-glm53-logs/extra-probes.mjs`（沿用历史负例的 vite 内存构建模式，不写源文件、不依赖浏览器），实际运行**全部通过**（exit 0）：

- A：非对象 JSON 载荷 `[]`、`[1,2]`、`null`、`123`、`"text"`、`true`、嵌套对象、数组值、`1e400` 全部被拒（无 z.record 静默折叠成空对象）；
- B：载荷键 >200、值 >2000、键数 >100 拒绝；恰好 100 键通过；
- C：事件 0 条与 101 条拒绝；恰好 100 条通过；
- D：保留键对象值/数组值、`\u005f_proto__`、`\u0063onstructor` 转义变体全部拒绝；近似普通键（`proto_value`、`__proto__value` 等）完整保留；
- E：priority ±1000000 通过、1000001 拒绝；条件 51 条、动作 101 条拒绝；`always` 夹带额外字段 schema 拒绝；
- F：stale 无说明、completed+committed=false、unknown 字段、actions >10000 全部拒绝；
- G：非对象服务返回拒绝显示；无 refresh 服务时 refresh 无害空操作。

## 5. 历史三项 P2 逐项核验（结论：全部确认关闭）

| 项 | 原缺陷（ui-local-review-1.md） | 本轮独立核验 | 判定 |
| --- | --- | --- | --- |
| P2-1 无额外条件无法表达 | conditions 只有 equals/exists/type 且 min(1)，G-behavior 行为 X 无法忠实表达 | model.ts:13 新增 `{kind:'always'}` strict 成员；BehaviorWorkspace.tsx:622/628-629 显式"无额外条件（恒真）"选项并隐藏对象/属性字段；validateDraft:247 对 always 跳过对象校验且不要求伪造字段；空数组/缺字段/always 夹带额外字段仍拒绝（单测 154-172 行 + 探针 E）；宿主 onDraftChange 与 runSample 收到精确 `{"kind":"always"}`（单测 + 本轮 headless 实测通过） | **关闭** |
| P2-2 矛盾证据组合被接收展示 | candidate+applied/recorded 等 state/committed/error 之外的矛盾可通过 | model.ts:158-186 superRefine 增加单轮动作/通知状态矩阵（candidate: planned/deduplicated/skipped+candidate；completed: applied/deduplicated/skipped+recorded；failed/cancelled: rolled_back/skipped+discarded），与 README 表一致；测试 281-337 行遍历全部 4×5×3=60 合成组合精确断言每个组合的通过/拒绝，四状态 controller 矛盾拒绝 + 矛盾刷新保留上一有效结果（338-355 行）实测通过；committed=state==='completed'、failed⟺error 一致性保留 | **关闭** |
| P2-3 保留键静默丢值 | z.record 归一化丢弃自有 `__proto__` 键，两份不同载荷折叠为空对象且照发 callback | model.ts:284,308-319 在 z.record 之前检查 `Object.keys`（JSON.parse 产生的自有键，含转义形式）三类保留键并整体拒绝，编辑原文保留、`return` 不入 parsed；单测 359-396 行验证两个不同 `__proto__` 载荷均拒绝且 callback 零调用、普通字段无损；探针 D 扩展 5 个变体 + 近似普通键保留全部符合预期；本轮 headless 对两份载荷逐次点击执行实测"显示保留键问题且测试调用次数不增" | **关闭** |

历史不通过报告（`/tmp/T06-UI-571b4d6-independent-review.md` 即 ui-local-review-1.md）未被覆盖或改写；571 提交、旧 verification Git 对象与全部原始证据哈希均保持不变。

## 6. 全范围对抗审查结果

按派发"完整对抗审查重点"清单逐项核过（对应源码行为已在 10 文件全文阅读中核对）：元数据完整性（schema strict/min/max/enum）；行为 ID 唯一与 `editingBehaviorId` 例外（model.ts:242-243）；单组 AND 与冻结快照文案；四类安全动作、上下移/移除重排（move 边界正确）；单值关系追加与多值覆盖分别拒绝（272-277）；对象/类/属性/IRI 已知性与同实例先创建后引用（`known.add`，264-270）；有序事件与显式 add/remove/set；批内重复 ID 拒绝而重放引导"重复运行原事件"；请求 `structuredClone` 保真（callback 变异不影响 controller，单测 482-492）；UI 不重做领域引擎（validate 边界文案明确推理/幂等/竞争归隔离服务）；逐条触发原因、动作顺序/状态、Diff、通知、request/run/断言/推导/语义版本全展示；候选/提交/失败/取消与当前/过期/历史组合安全文本；单轮不混旧轮（矩阵+注释）；未知字段/evidence 拒绝；React 文本渲染 HTML-like 通知不执行（本轮 headless 实测 `img==0`，且新截图确认 `<img src=x onerror=alert(1)>` 以纯文本显示）；异步 epoch/卸载/能力变化/四字段切换迟到回包拒绝；同项目（含输入版本）刷新保留草稿、切项目重建（README 责任 + key 约定）；refresh 只读同 runId 不重发不覆盖；cancel 必须真实终态、ack（`{accepted:true}`）不当取消、完成/取消双向竞态正确（cancel 中 epoch++ 使迟到 run 回包失效，run finally 清 pending 使迟到 cancel 回包失效；本轮 headless 实测"取消等待确认+拒绝迟到完成覆盖取消"）；缺省无服务禁用；固定 5 项错误枚举 + 本地说明，原始异常/路径/敏感值不回显（单测 472-481,528-535 + headless 无 pageerror）；scope 标签仅提示非权限证明；onDraftChange 仅通知非保存；1440/390 布局无横向溢出（脚本 scrollWidth 断言 + 本轮新截图实际查看）。

**新发现：无 P1/P2 缺陷。** 信息级观察（不构成阻断）：

1. [信息] 列表渲染使用 `key={index}`（BehaviorWorkspace.tsx:172,219,338,364）：删除中间条目时 React 复用节点可能造成输入焦点跳到相邻条目；value 驱动渲染保证正确性，仅影响焦点体验。建议后续接线时改用稳定 key。
2. [信息] `verify-headless.mjs` 的 fixture 服务返回按当前 UI 语言文案精确匹配按钮/文本（如"在隔离副本中测试"）；若后续文案微调需同步脚本，属维护性提示。
3. [环境事实，非产品缺陷] 本审查树 `npm run check` 原样 exit 1 系证据解包目录被 lint/format 扫描所致；owner 若需原样绿，可将 `ui-review-evidence/` 加入忽略清单（属审查树准备面，不属受审 10 文件）。

## 7. 未验门（继续列明，均未因本轮关闭）

- 真实 App 装配/bridge/preload/CSP 接线；真实引擎/Store 事务、推理、幂等与竞争领域执行；真实 G.3 基线（B-01～B-11）经 UI 驱动；Agent/G.5；原生 Electron/macOS/Windows 与包内验证；另一指定模型（MiniMax M3.1-Flash）同版审查；CI/推送/PR/合并/发布；真人验收。私有 callback 与开发夹具不是上述门的证据；FR-600–604 父模块验收不因本组件子阶段通过而关闭。
- 历史遗留已知缺口维持：历史浏览器 binary SHA/完整 argv 未记录（不从当前推断）；本轮使用的 1248 安装由 owner 经官方 GCS JSON 入口完成而非官方 CLI marker 形态（已记录差异，实测运行无影响）。

## 8. 本轮产物清单（本树 `test-results/t06-ui-zcode-glm53-logs/`，均 gitignore，不覆盖任何历史输出）

| 文件 | SHA256 | 说明 |
| --- | --- | --- |
| vitest-unit.log | `43a62f93…2e8ed` | 专项 34 单测 exit 0 |
| check-full.log | `77880e3c…7b7bcb` | 原样 npm run check exit 1（首败=lint 证据污染） |
| eslint-excl-evidence.log | `e3b0c442…b855`（空输出） | eslint 排除证据目录 exit 0 |
| format-check.log | `d9314d35…d0ec9` | prettier 原样（仅证据目录 8 文件警告） |
| typecheck.log | `ef35be54…1e55d2` | exit 0 |
| npm-test-full.log | `950223b2…48eabe` | 664/664 exit 0 |
| build.log | `5e6d8d49…b6d4710` | exit 0 |
| engine-check.log | `82a1d258…3c7bcb` | 1052/1052 exit 0 |
| browser-install-attempt5.log | `cb35e882…658` | 第 5 次官方安装失败 ECONNRESET（保留） |
| extra-probes.mjs / extra-probes.log | `3ffce215…f57` / `be607a4c…3fda9c` | 补充只读内存反例全过 |
| verify-headless-zcode-glm53.mjs | `31912868…8967` | headless 重定位副本（仅 component/output 两行差异） |
| verify-headless-copy.diff | `30c55866…52ef` | 副本与原脚本完整差异 |
| r3-headless.log | `2d566b6f…d65` | 完整 headless 正反例 exit 0 |

新输出目录 `test-results/t06-behavior-ui-zcode-glm53-r3/`（本轮唯一，未覆盖历史 r1/r2）：evidence.json `d7397917…0b56`、width-1440.png `da427422…b04`、width-390.png `8dcbe971…4a6`、viewport-390.png `570922bd…d30`，及由脚本本次实际生成的 fixture 构建产物（preview.js/preview.css/index.html/debug-structure.txt）。

## 9. 环境事实补充的接收记录（2026-10-22 用户第二轮消息）

- 用户纠正"只能 1248、禁止 1208/1217/1234"系派发补充自加限制，非原用户硬门：已接收，本报告不以默认配套版本充当产品门；本轮实际即默认 1248 路线，无版本替代。
- owner 经官方 GCS JSON API 同对象入口下载安装 1248 至本树：我方只读核验了 findings.md / source-and-network-findings.json / owner-install-receipt.json 与本树二进制（哈希/版本/权限/16 文件），安装与版本读回不计作验收——headless 全链路由我方按上述副本实际运行并 exit 0，方有本报告结论。
- 该消息不含其他模型意见；本轮全程未读取 S1 当前外审或另一模型输入/报告/会话。
- executablePath 例外路线未启用（默认路线 launch 与完整验证一次通过），故无临时 runner diff/argv 需记录。

结束状态：HEAD 仍为 `3b3af941c73b7a5d416fda50ec6fb8102992551f`；`M AGENTS.md`（未暂存保留）；未提交、未推送、未切分支、未修改任何受审源码/测试/配置/锁/共享文件/另一模型文件；仅更新本报告与上述 `test-results/` 下本轮临时输出。受审内容任何变化均须双方新建同版完整审查。
