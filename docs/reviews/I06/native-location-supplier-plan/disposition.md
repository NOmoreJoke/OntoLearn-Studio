# Native 位置供方静态方案：意见处置与交根请求

2026-10-21。本件仅处理本轮指定新 docs。主稿首审48256B/SHA256 `ff21c9f0c10d2f40e48d5f93dbccdd880523ec03327bd687eb3c997545afb518` 已逐字保存在 `main-plan-review-input.md`；最终修订49472B/SHA256 `34c4307e42c349b5d4fc40d0960655454727570eb565c4fc1c3d521663c57624`，最终定点回读原文见 `independent-review-followup.md`。本文件不冒充产品/native审查或实施批准。

## 1. 实质调查与路线选择

T01固定379916合同及423b真实源码揭示：首次mkdir/writer-lock/connect都尚无物理能力；备份xb后connect/rb/fsync/read_bytes重复path reopen；普通backup另有connect；close失败仍尝试释writer lease；main stop没有真实child/管道/Store排空聚合。不能只在main加stat后继续原路径打开。来源逐路径bytes/SHA与准确行号完整保留，没有把后续可变T01源码先行采用。

平台原报告优先自有CPython连接适配；主稿比较当前T01 stdlib消费面后选择“受控重建 `_sqlite3` 与私有注册扩展同一SQLite image”。理由是保持现有DB-API/事务/backup语义、缩小业务消费替换面；代价是T03需掌握Python/SQLite构建分发闭包。此为工程选择，不是已证明的安全/性能优势。平台原意见保留，不改成同意主稿；任一路线都仍需同image/VFS真实trace，不能另一库注册同名充证明。

官方source补充记录了CPython实际open/close、SQLite接口/3.51.3候选/许可证及ACL快照边界。SQLite完整os_unix/os_win原文当前未取得，Fossil/Raw读取失败、GitHub部分展示没有提供完整函数覆盖；T03固定源/精确补丁审查是N1硬输入。输入定位曾尝试在e2c读取位置offer，Git明确不存在，已正确改用真实文档ref `1f3b053d8a69d1f7ddb1e29c143f648d910fe689`，没有把后写设计说成e2c产品。

## 2. 独审意见逐项处置

首审原文12009B/SHA256 `a6d67cb636a3183eced3cfb64383823bd49d038832252fc75cb8e0a19135092c`，由独立agent `/root/i06_design_review` 对主稿ff21及完整来源报告进行。结论无新增P1/P2，D1/D2为P3文档精度问题；所有既有生产前置仍保留。首审原件与格式canonical分别存储，最终身份见manifest。

| 意见                                                                                      | 具体修订                                                                                                    | 证据/边界                                                                                            |
| ----------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| D1：原生flags中的bitwise pipe被Markdown当表格分隔，原语/Windows/拒绝分支错列              | 主稿“独占建立”重建为完整四列，并转义pipe；平台报告3处表达式的7个pipe转义，重新对齐表格                      | 静态逐表检查主稿及平台所有连续表的各行列数一致；Prettier本身不能发现该语义错列。原ff21与平台fd09保留 |
| D2：N0“前三类测试”与第三行VFS排除矛盾                                                     | 改成精确6产品、3测试、3T03新构建路径名单；明确排除Python/VFS/patch及T01共享路径；其他既有构建delta须T03再列 | 仅范围澄清，不新增代码/窗口，不授N0实际实施或SQLite IO                                               |
| 审查建议：跨process消息/ancillary、FD/HANDLE/map/queued-work容量与同步接纳点需落实有限ABI | 主稿已要求原生reserve/gate/全部实际资源与无超时清槽；正式ABI冻结时由I06/T01/T03逐项收敛                     | 当前没有无限公开入口或已批准实现。此建议不是新增公共协议或实际磁盘quota，也不声称ABI已编译验证       |

自查附加修订仅两项：根审计SHA从前缀补全；补充held对象 `acl_get_fd_np`/`GetSecurityInfo` 与ACL快照不防并发变化的边界。输入清单仅追加B-M根收口docs ref/3077B收据身份；原首审19602B/SHA256 `0d31621bbde2fbf716fb06950ec842f3d554d529cb53ae1c16e83d463dd2b5eb` 精确保于 `inputs-review-input.json`。最终inputs19875B/SHA256 `54a32efe8d54ef2b0b2b0418f2abc6b63a6f3f5fd9dba86d698645d3e1538955`。不新增权限、不改selected路线或生产阻断。

## 3. 文档格式失败与原件保全

首个真正显式检查 `prettier --ignore-path /dev/null --check` 六件新docs实际exit1，仅T01来源报告格式告警。实际argv/cwd/stdout/stderr/exit保存在 `format-first.json`，不是产品测试失败。作者早前默认检查因路径ignored而未实际检查，不能计通过。

- T01首报告19310B/SHA256 `b2810c2c166d732c7422ee6361c80a98fb35647da9e1dda137e448ce202ff34c` 保 `t01-source-static.original.txt`；canonical仅Prettier对齐后24521B/SHA256 `c8a131db87d27b17f6a33f02b3074ed07c59a3309ce8b9b1ce3d342087947e96`。独审已按归一化布局与diff确认无实质变动。
- 平台首报告45555B/SHA256 `fd09ac310c543a8c85d29efb13b1155a4589e5cdf162e013a49f357e5c03d882` 保 `platform-static.original.txt`；canonical仅D1 pipe/布局修正后44109B/SHA256 `65a4e5fef210c6efa9f05fe33bef0f81fdf93a66063f5d414f10526b83af017c`。
- 独审r1首原文保 `independent-review-r1.original.txt`，canonical格式不改变意见与受审身份；最终followup不回写r1。原主稿snapshot继续保首审可重现，包括原D1/D2缺陷。
- 两份外部根材料原字节保 `authorization.txt`（5447B/15d40…）、`root-integration-audit.txt`（17048B/6f86…），完整身份在inputs。原B-M64及其manifest/ZIP不增改这些材料。

最终格式检查仅对canonical/new structured docs显式运行；`.original.txt`与授权/audit原件按原字节保护，不对其自动排版。snapshot仍是历史版本，格式pass也不表示其D1/D2正确。静态实际结果与范围保 `verification.json`，manifest自排除，不循环自认证。

## 4. 交根的准确窗口与仍缺供方

以下是**接口/实施请求**，均未向其他聊天发任务、未取得实际writer窗口。本次方案不是“native已派发实现”。

| 请求                          | 唯一owner及准确结果                                                                                                                     | 仍缺/准入策略                                                                                                                |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| N0受控临时对象底座            | 根确认主稿§9的6产品/3测试/3T03新构建名单，I06仅私有native供方，T03只构建/锁                                                             | 精确writer登记、工具链/两目标OS环境和运行授权缺失；当前继续静态设计，无SQLite/用户目录/生产许可                              |
| T01窄消费合同                 | main bootstrap/Supervisor真实nativechild transport/首次IO前接纳、真实stdin.write的原dispatch、Store/format3/backup逐重开替换、永久drain | T01唯一维护全部现有共享路径/公共canonical，不能由I06写或伪fixture补齐；原typed签名由owner确认                                |
| T03同库闭包                   | 主稿§8新构建4件及脚本/现有锁/入口/打包准确delta；CPython/SQLite源/hash/patch/SDK/runtime/产物依赖                                       | Node-API不认证SQLite/CPython；现uvPython/PyInstaller目录包不充同库或目标OS证明                                               |
| 原子namespace/alias围栏       | I06/native+平台供方说明实际OS保证与目标证据                                                                                             | mac heldparent不能阻止祖先/rename source被换；Win share/ACL也非全局证明。严格保证当前未交付即unsupported；不可自行缩威胁边界 |
| 跨崩溃oldchild/锁SHM          | T01实际child与I06真实holder/恢复仲裁                                                                                                    | main死、旧child/映射仍活时新main不得因控制锁已取/PID缺席/abandoned而开新writer；当前是生产硬阻断                             |
| B-R fresh/历史/唯一安装writer | T01+安装供方给稳定实际appData/产品/OS principal/多安装与迁移来源；I06做固定控制协议                                                     | 没来源不ENOENT=fresh，不新增项目/Job/main账本，不全盘扫描或删历史                                                            |
| 目录项耐久与恢复              | T03/平台给macOS15 arm64与Win11x64真实普通权限/受支持FS保证                                                                              | 文件flush/close/rename不认证父目录项掉电耐久；缺durable intent+seal不授其他目标mutation                                      |

N0对象级底座可以独立申请；N1同库/真实child需要完整源与消费合同；N2生产fresh/控制/Store/dispatch闭包还受上述所有前置。每阶段单独授权/实际验证，不自动晋级。窗口缺失不会重建原Goal，不把八模块独立工作全停，也不会因B-M已收口降低原合同。

## 5. 冻结与门

本轮仅新主稿及专属新来源/独审/处置/manifest。24固定Git输入、4规则输入、B-M64和3077B根回执逐字/哈希核验；实际检查以verification为准。提交相对 `6240748d83d2251664b3fe1e9808f5f67adeec41` 只新增native docs，不夹带AGENTS或任何产品/测试/构建修改。B-M根回执另在6240748纯docs提交，原产品仍固定fa8。

没有运行产品、测试、native编译/实验、用户目录、GUI、Keychain或模型；未重测无变化B-M，不借旧713/1052等数字当native证明。完整父I06/57P0、指定双模型同版外审、目标OS/真人、CI/正常合并/远端门均未关闭，不推送或更改Goal。
