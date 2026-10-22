# 六树 setup 完整独立审查

结论：**SETUP_NEEDS_CHANGE**。候选 `e95f20f3db8a5fe84450e1d72810d7371cef79f1` 有一项 P2 环境隔离缺口；修正后需核对该精确 delta。本报告只评六树 setup 与发审输入，既不是三个产品的通过结论，也不是 ZCode/MiniMax 指定 Pass。

审查者：独立 Codex agent `/root/t03_physical_setup_independent_review`。原作者未参与本报告写作，未向审查者提供希望通过的结论。未创建外审任务、未读取任何指定模型本轮任务/意见/状态、应用 runtime、配置数据库或停止 Caller/fee WIP。未安装、未运行产品/check/sources/e2e/build/fixture/package/probe、未导入或执行本包的 setup 工具、未提交。唯一新增本报告与 `independent-review-checks.json`。

## 固定输入与完整读取

仓库为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping`，候选实际 HEAD 等于指定 e95；分支 `feature/weekly-t03-mapping`，候选初始状态仅 AGENTS.md 未暂存修改。候选 37 payload / 457375B 与 manifest 9239B 全部从固定 Git 逐件核 bytes/SHA，并与当前工作文件逐字核同；manifest SHA256 `a61642c73c681606aa356c83e413422e9eb22287b4b6bda68465f33d011b6ad0`。完整输入身份记录于本报告旁的 checks JSON。

已完整读取 README、静态命令审计、bootstrap/make-prompts/seal-setup/validate-package 四个文档工具、candidate manifest、注册 roots、prompt index、全部六份 before/after/after-first-inventory、isolation receipt、Electron installer 静态收据、两次文档检查首失败与修正结果。18 条原位安装日志均完整读取并逐字等于 after 收据 fullText，bytes/SHA 也吻合。所有新 JSON 均由独立 stdlib 解析，所有新 Python 工具均由独立 AST 解析；没有运行作者验证器来代替审查。

六份完整提示均读取并核字节。重复的执行补充逐份核路径/HEAD/product/模型映射，归一化这些已逐项核对的变量后全文相同；三份共同规则在每份提示内各完整出现一次，逐件等于当前原件。三组冻结 zcode 原文已全文阅读，同组 minimax 的全部差异仅为角色标题、目标模型/思考/权限与报告建议文件名，差异全文核阅；每份实际新提示的完整冻结 suffix 均从指定 offset 起逐字等于对应 dispatch-v2 原文，未仅以摘要代替全文。

原旧包 36 payload 与 final-preparation self-manifest 全部保留，后者 SHA256 仍为 `818f767ac872fabb585f911e029022ed24392abb94ed3561a6c8f20b3deb23d5`。未读取其中受限 archive/SDK 身份载荷；核的是原已批准包的文档身份，不声明重新审读产品全部历史载荷。

## 唯一发现

### F1 / P2：清除或固定继承的 C1 证据输出路径

位置：本包 `bootstrap.py:65-86`，及由它生成的六树 `build/review-session/environment.sh:3`；对应正常未改消费者为各树 `tests/e2e/csp-lifecycle.spec.ts:308-317`。六份提示 `:28` 要求运行前 source 该环境，`:46` 又限定只向自己任务输出面写入。

触发：外审应用/终端继承某次旧 C1 运行的 `I02_EVIDENCE=/旧树或同伴路径/evidence.json`，再 source 当前物理树 environment.sh 并按后续正常阶段运行 `npm run test:e2e`。环境脚本既不 unset 也不将 I02_EVIDENCE 指向本树；原 C1 测试从 `process.env` 拷贝它，在 finally 中直接 mkdir/writeFile 两次。

影响：即使 Node/Python 依赖与 TMP 完全隔离、GUI 已获总控运行 lease，C1 仍可写出本任务唯一输出面，覆盖旧证据或污染同伴目录。这是确定的静态数据流；本审查没有通过运行 Electron 复现，也没有读取当前父进程该变量值，因此不声称已经发生越界写入。

证据：全部六份实际 environment.sh 均未出现 I02_EVIDENCE，bootstrap 的 clear 与 values 也没有该键。消费者代码明确使用 `if (env.I02_EVIDENCE) { mkdir(resolve(env.I02_EVIDENCE, '..')); writeFile(env.I02_EVIDENCE, ...) }`。九个正常配置/脚本的 Git blob 在全部六树相同，故不是单树偶发差异。`I02_NATIVE_EVIDENCE` 在本正常 C1 路径被 `runNativeRecovery(..., { ...env, I02_NATIVE_EVIDENCE: nativeOutput })` 明确覆盖到 tmp 下本次唯一文件，**本发现不把它误报为同一逃逸路径**。

建议：在 owner 的 setup 环境生成器中将 I02_EVIDENCE 显式固定为各树自己的 `build/review-session/raw/c1-evidence.json`（或清除后明确按单次运行分配本树路径），同步六份实际环境与精确提示映射，保留本候选/首 Fail 原件。用人为设置旧值再 source 的纯 shell 环境回读核六树最终输出路径即可；不需要运行产品或重装依赖。随后封存新 delta、核全部受影响新文件 bytes/SHA 与原 suffix，并由独立审查关闭本项。

## 已核成立的范围

六个物理树均是注册的独立路径，实际 detached HEAD 分别为两份 mapping `0fb8e045ec776da6e8dc1b306c72212982114cd8`、两份 selection `4fa5d62eb13269351384527b1f84761c08811e79`、两份 profile `56a852321d72c6665044242d24064bf3523302d3`。每树工作区仅有 AGENTS.md 未暂存修改，15147B/SHA `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`。reviewHead 相对各 product 的非 docs、非保护 AGENTS 产品路径无差异。

六份 .venv 均为本树实体目录，editable `.pth` 精确指自己的 engine/src；普通开发引擎确实硬使用本树 `.venv/bin/python`。profile build metadata guard 也要求 sys.prefix 和 distribution 文件解析后属于本树 .venv，故采用树内实体环境有实际必要。18 条 setup 收据 argv、cwd、时间、exit0 与原位 metadata 相同。安装日志的 Python 分发数分别 17/14/19，与当前 macOS 平台收据一致；未将它们混作跨平台 lock 全量条目。

独立全量 lstat 范围仅为每树 node_modules、.venv、build/review-session。普通文件 inode 跨树碰撞 0，普通文件 nlink>1 为 0。各树实际 regularFiles/bytes/directories/symlinks/unique inode 数与封存 after snapshot 均相同；详情见 checks JSON。18 个外指 symlink 均为每树三个基础 Python 链接，最终指同一只读基础 Python；其余链接留在各自树内。未借同伴依赖目录、未读取同伴意见。这些是逻辑目录项观测，OS/app 实际 metadata 操作次数仍为 UNKNOWN，不能拿它给停止 Caller 补账。

正常 root/desktop scripts、builder、Playwright、C1、I04、native-driver、fixture 和包内验收脚本已静态核；这九项 Git blob 在六树分别一致。`check` 包含真实子进程与 SQLite、构建，并非纯静态；sources 脚本读取原 manifest 列表；e2e 会安装并启动真实 Electron；package 是 unsigned 目录包，包内回归另有明确脚本和新输出目录。未把 package exit0 当作包内样例或两 OS 通过。

C1 runNativeRecovery 没有 Linux 或 I02_NATIVE enable gate，Mac 默认也执行；普通未改 C1 不被 T03-N0 禁票泛禁。I04 reload 需本次 fixture、coordinator 需 Linux、real-native 还需 I04_NATIVE_ISOLATED 与其 display/window 前提；提示准确保留这些条件与 Mac skip 的含义。I02_HMR 改源禁令仍在，C1 既有 hook 自动答复局限亦已披露，未冒充真人原生验收。

默认 Electron userData 没有由 worktree/TMP 自动隔离：main 使用 `app.getPath('userData')/engine.sqlite`，初始 launch 未传独立 user-data-dir。提示 `:36` 与 README 准确写为后续总控资源前置；本包没有声称已隔离或准许现在运行 GUI。因此此已知前置不另列为 setup 虚假通过问题；获得未来实际运行条件前仍不能以本 setup 证明可以安全并行开应用。

未签 N0 native/producer/caller、受限 SDK/identity payload、被拒资源研究、HMR 改源、付款/密钥/抬 guard 均未因新权限扩张；原 Caller 停止现场明确禁读写。原组专门 probe 重跑仍要求冻结 argv 与对应阶段边界核对，未转成任意工具执行。实际 task/settings/lease 均为 null，不伪填目标设置；普通运行与 app 创建/读回 lease 由总控后续安排。六份报告/raw/metadata 写面位于各自物理树，禁止窥探同伴当前意见/状态的规则完整。

## 首失败与验证限制

作者两次文档工具首失败均保留：inventory basename 判断错误的完整 18 链接与结构化处置、首次六份 snapshot 留存；原完整 traceback 指向原 Codex tool chunk，未伪装为入包 verbatim raw。editable .pth 名称误猜的完整终端文本已入包，后来仅检查器路径改正。它们都是本次 setup 文档工具错误，不是产品失败。独立静态阅读时，我曾在物理 mapping 审查树猜本包相对路径，两个 nl 报不存在；随即从外部共享 mapping 包绝对根重读，完整行号已核。该读取错误未触碰产品、未产生产品运行结果。

独立复核只运行 Python stdlib 文档解析、哈希/字节核对、只读 Git 与 lstat，没有调用作者 bootstrap/seal/validate 工具。未实测任何产品功能、性能、UI、native 恢复或 package；第三方 installer 的所有 transitive 实现没有穷尽审计，未承诺零 OS 操作或无网络。全部指定模型、父业务、两 OS、真人、签名、CI、远端和发布门继续待其原有证据。

原 38 件候选可作为首次审查固定原件保留；F1 关闭前不建议把它标作最终 setup-ready 发审包。除此项外，本次限定范围未发现新的阻断发现。
