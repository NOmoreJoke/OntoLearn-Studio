# MiniMax 本轮 F-1 独立静态 triage

2026-10-23。结论：F-1 的核心技术点成立，保留原【中】及 OPEN；exit 2 的 fail-closed 行为仍正确，问题在 stderr 固定错误面和路径暴露，不是错误输入获准发布。过程越界异常与技术发现分别待根处置，不能互相抵销。本意见不关闭旧18项或新F-1，不构成指定双审通过。

## 范围与证据

仅通过文件读取核对 owner 树 verify-release.mjs、verify.ts 开头、专项 CLI 断言、既存 owned-fixes/verification.json 与其 tar.gz 内获准的 final-expanded-unit.log / final-full-check.log，以及固定 M 报告 F-1 段及相关汇总。没有执行 shell/CLI/测试/安装或任何复现命令；没有访问 native 源、tool 返回、原 runtime 报告、GUI、DB 或全局配置。归档仅在内存解析，没有提取落盘。

固定 M 报告路径：docs/reviews/T11/fresh-review-minimax-completed-20261023/minimax-report-original.md；读取字节为48446B，SHA256 60757b59116f5a4446adf6011a9fae445f719168d5709ff396dabf191a9f1b34。以下报告行号均指该原件；报告本身不改写。

## 成立程度

1. verify-release.mjs:1 在主 try/catch 外静态导入使用 ESM 语法的 verify.ts；try 从第11行开始。历史 final-expanded-unit.log:17–21、39–43，及 final-full-check.log:55–59、77–81，均保留 MODULE_TYPELESS_PACKAGE_JSON 警告、绝对源码 file URL、package.json 路径和最终固定错误码。这是允许历史原件中的实证，不依赖 M 本轮受限调用的返回。
2. 当前 tests/unit/t11-release.test.ts:1188–1190 只约束 exit=2、空 stdout 和 stderr 最后一行。它不能发现固定错误码之前的警告/路径；1193–1207 的“不含 sensitive”也只保护样例输入字面，不排除工作树路径。因此当时把断言改成末行匹配，使工程检查通过，但没有消除该警告成因或建立完整错误面保证。此前本内审将其作为 Node 警告与断言兼容性处理，未把固定错误面另列，现补充为明确未决技术项。
3. 模块类型探测发生在入口主体执行前；仅将普通错误 catch 改写或在导入后添加过滤，不足以证明警告已被控制。历史警告直接诊断“未指定模块类型、检测到模块语法后重解析”。本轮未额外读取根 package.json，故“根配置无 type 字段”的独立源码核验仍由配置 owner 做，不能把 M 的 grep 自述冒称本审者已执行。
4. 历史证据足以证明该候选在既有 Node 环境出现额外 stderr 与路径；不外推所有 Node 版本/启动参数均如此，也不采用 M 本轮自述的625B/5行作为已独立认证计量。未见由此接受坏证据或改变 releaseAuthorized:false 的依据。报告第274行“退出2”文档本身并未因此失实，应把缺陷聚焦在完整 stderr/固定错误面，而不是退出码。

## 报告引文与计数纠正

- F-1 第258行把 import 引为 verify-release.mjs:16，实际为第1行；第16行是 verifyManifest 调用。tests 第1190行引用正确。
- 第169行表内 #1 是基线正例 consistent=true；第170–182行才是13个负例。第142、184、208、283行“14组全部拒绝”应区分为“1正例接受、13负例按预期拒绝”。本轮只核报告内部表述，不认证自建探针实际运行。
- 第11行称4个脚本，但第122–126行列出 collect-macos.sh、collect-windows.ps1、pe-machine.ps1、verify-release.mjs、verify.ts，共5个。
- 第199行是默认 check 的735 passed +4 skipped；第202行是显式 flag 的739 passed /0 skipped。第337行须明确其“含探针”结果引用 C4，不能让读者把 C1 默认运行也读成零skip；这不是两个结果数字互相矛盾。
- 第281行未来验证不宜把“专项109”固定成验收上限；新增回归后应按新候选实际数量、显式flag/skip和完整命令记录。上述报告误差不推翻历史原件支持的 F-1 核心。

## 最小修复方向与协调

优先消除本线入口的模块类型歧义，保留固定错误面。可由 root 批准精确 owned 配置路径后，评估 scripts/release 局部 package scope 明确 type=module，或明确 ESM 的构建/入口方案；这只是静态候选方向，尚未试验、未宣称可直接通过。不要为这一局部问题自动修改整个仓库根 package.json。

若选根 package.json 的全局 type、共享 tsconfig/构建/锁/CI 方案，须 root 协调各共享文件唯一配置 owner，评估现有 CJS/ESM 调用面，出新候选后按真实影响验证。本线不得自行接管共享配置。新增本线 package.json 也须精确路径授权并进入冻结/检查范围。

恢复整段 stderr 严格断言，使无法读取、格式错、超限两入口等错误路径只含约定固定错误码与允许换行，空 stdout/exit2继续保持；同时排除 MODULE_TYPELESS_PACKAGE_JSON、源码/输入绝对路径和输入内容。普通参数错误与合法 synthetic/evidence 输出的既有行为也要保持。后续由 owner 在获准边界运行显式固定专项与完整 check，按新实际计数记录；本次不执行。

不将报告第280行“保留警告并披露”直接当修复通过：文档披露不能自行取消固定错误面要求；全局 --no-warnings/NODE_NO_WARNINGS 也会遮蔽其他诊断。若选择特定警告控制，须证明在模块加载前生效、范围准确且不丢失其他必要诊断，仍以严格完整输出回归为门，不能仅保留末行断言。

## 处置状态

F-1 保持 OPEN，待 root/唯一 owner 决定方案及精确配置责任；18项历史处置和正式 NotPass/双审门不由本静态 triage 改写。input-only 越界及 owner 回读异常继续 OPEN；未读其返回，不把报告的 collector/hook 断言作实际执行证据。技术修复、新候选、新验证和指定门禁独立继续。
