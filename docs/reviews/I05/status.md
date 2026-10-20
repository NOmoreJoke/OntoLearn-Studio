# I05 / B1 状态

日期：2026-10-20，Asia/Shanghai。开发会话：`01a15744-136d-7000-abad-46de101eadaf`。

当前阶段：总控追加的 Q6 差异表、真实两范围、错误来源细分和首次工作负载补充已形成 `independent-v3` 证据，已完成真实源码 / 包内验证。完整 Goal 工具仍为 blocked；本轮补充取得独立进展，不表示完整集成目标完成。尚无正式集成候选、指定双审、推送/PR/合并。

- 唯一工作目录：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-semantic-validation`。
- 分支：`feature/I05-semantic-validation`；初始 base/head：`1b6df7a220fc9a67d7046133a340085f03f0a96c`。origin 为 `https://github.com/NOmoreJoke/OntoLearn-Studio.git`，启动时远端 develop 与 base 一致。
- 已读取总控最新 goal/scope/policy/parallel/state 和 before-I05 两清单；PRD V0.6 C/D/E/G、B1 原文、S1 口径及 ADR/退出证据。
- 既有唯一 dirty 文件 AGENTS.md 属他方操作规则；SHA-256 `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`，与原仓库最新指南一致；不 stage、不修改。
- 原仓库 I02 冻结与 I03 worktree 均不写入；总控 state.json 不写入。独立 node_modules/.venv/build/release/临时数据，无共享可变环境或产品端口。

早期独立实现检查点为 `02a8c90902788963206d7ef60fbeccc801e27c5c`；本轮 v3 实现包含后续真实语义修订，最新本地实施提交以 `checkpoint.json` 为准。受测源码固定哈希见 independent-v3，全部未推送；不表示正式 I05 审查候选已齐备。

本轮受测 base 仍为 `1b6df7a220fc9a67d7046133a340085f03f0a96c`。总控通知 PR3 已合并后，本会话 `git ls-remote origin refs/heads/develop` 实查为 `c2f9b038b23f9f48cdbb8f433a89b55a00edc9d3`。按总控授权完成固定来源的 v3 测量；正式集成前刷新实际新基线，不将 I02 写为仍阻塞。I03 正按新基线重验 / 冻结，真实 I04 仍待其完成。

## 范围、责任与依赖

本会话唯一维护 Python 依赖/uv.lock、纯语义模块、专用测试/探针、必要 PyInstaller 配置与 I05 证据。协议、存储、失效码、共享契约与能力注册表、主进程/preload/renderer 由其他线负责。

独立阶段固定真实 RDFLib/pySHACL，有限子类/domain/range 闭包后单阶段规则、真实 SHACL 模板与查询；拒绝 SERVICE/FROM/隐式外联；同样例源码与包内执行，复用 S1 两档口径并补充语义阶段与完整依赖证据。只做候选技术验证，不实现课程、业务 UI、映射/行为/沙盘引擎或模型外发。

I03 同版本契约设计合并后对齐纯接口；I04 常驻任务系统合并后，必须补齐真实任务语义、持久化/取消/错误/包内及窗口边界联验。不得用 stub 替代；当前纯模块不进入 health 能力声明。基线变化后重新验收和双审。

## 验证与审查

- 独立只读 agent `/root/semantic_boundary_review` 完成早期六项、浮点归约及本轮范围 / 错误 / fresh / Q6 复核；实际发现已修复并定向关闭。最终完整输出保留的 scopes 定向复核 14/14 通过。完整过程见 [internal-review.md](internal-review.md)，不替代指定双审。
- 最新 `npm run check` 通过：4 TS、322 Python（含 124 项语义测试）、lint/format/type/build；verify:sources 核对 12 份原归档。真实 package:dir 与同包 CLI 同样例/完整结果比较通过。
- 两档 18/180 断言、4 ontology、9/81 RDFS 推导、1/10 规则结果，源码/包内各三重复共 12 条原口径测量，另有 12 条 fresh-process 测量（每条 First / Warm 共 24 份完整观察）；首份到达、阶段与整进程退出分开。每运行时 28 个拒绝/库级 guard 用例；本地接收端正向校准 1 次，拒绝请求命中 0，入口 socket/DNS/urllib 尝试 0。
- 实际 engine 目录 36,693,213 bytes，未签名 app 558,389,705 bytes；完整依赖/插件/资源/导入/动态链接与许可、原始测量/命令日志/哈希见 [v3 独立证据清单](../../iterations/I05/independent-v3.json)。设备 Apple M5 Pro/64 GiB/macOS arm64，数据仅对应该机；无容量通过线。
- 依赖原生许可已核对官方 PBS 20260203 CPython3.12.12：full/stripped/本机库的 15 个内容段逐段匹配；完整文件哈希因 strip/安装路径不同而不同，不宣称字节相同。包内附 19 份上游 native 许可、完整元数据与来源；Python 锁依赖含工具/传递依赖的 36 份许可文件另列。上游 zlib-ng 许可路径缺失但实际为 system libz 链接，例外如实记录。不同平台原生来源仍待匹配。
- ZCode GLM-5.3/最高、MiniMax M3.1-Flash/xhigh：尚未创建本轮任务、无报告、无通过结论。正式全范围候选依赖实际集成完成；当前无安全 UI 环境，保留待操作。
- 本机仅无窗口 CLI/静态/单元/构建及未签名打包，不启动 Electron/e2e/native/HMR，不 Raise/点击审查应用，不自动启动产物。
- Q6 的 12 项原要求 / 候选差异 / 反例 / 影响 / 待采用修订淘汰登记见 [Q6 差异表](../../iterations/I05/q6-candidate-differences.md)，明确 FR-505 比较与同规则多结论未覆盖。合法两范围不再被误说为不支持；可信事实 / 公理错层属于适配错误，细码见 [v3 交接](typed-reasons-v3.md)。Q2/Q5/Q6 等产品决定、首发平台、签名安装/干净设备、容量结论和生产证据均未取得。

下一步：保存独立检查点，待 I03 同版设计冻结/合并和真实 I04 基线就绪，继续同一 Goal 的任务/持久化/取消/错误/包内/窗口联验。I03 当前错误/快照/依赖草案已收到，尚未当作批准接口或写入共享注册表。完整功能验收、同版本指定双审通过、意见全部处置后预约总控串行集成，再 PR→develop、CI 全绿、正常合并及远端核验。

## 历史续跑接口审计（v2）

核验 I03 实际候选 `6f35ffd` 仍待指定双审/合并，远端 develop 仍为初始 base。已逐码核对 30 个内部语义错误与 I03 草案，交接文档提交 `baa8c8b`，见 [contract-handoff-2026-10-20.md](contract-handoff-2026-10-20.md)。输入/结果/工作量资源分类、部分有限构造分类及非法词法与超范围字面量区分仍需唯一维护者协调，已正式交总控；未修改受测实现或共享契约。

本轮属于实际接口审计进展；前轮为实现/打包/证据进展。真实依赖和无干扰外审环境仍未就绪，未重跑无变化测试、未发起 GUI、未推送。准确恢复条件保留为 I03 同版设计双审合并、真实 I04 基线可用，以及两指定应用的新任务可在已核验无干扰环境执行。

## 历史连续阻塞审计（v2）

同一前置阻塞连续三个 Goal 回合仍存在。最新正式 wait_threads 返回 I03 任务已结束并明确报告 Goal blocked；远端 develop 未包含其候选，I04 仍未就绪。独立实现、包内测量和具体接口交接均已保存，受测源码/原始证据哈希再次一致。已通过 update_goal 将本会话标记 blocked；不是完成或暂停。详见 [blocked-audit.json](blocked-audit.json)。

恢复后继续本会话和完整原目标：取得真实 I03/I04 集成基线与无干扰指定外审条件，再做实际联验、同版双审、CI 与远端合并核验。未推送，不重启替代任务或操作用户桌面。


## 本轮补充交付与恢复边界

上列 v2 接口 / 阻塞审计保留当时来源，不用来否认后续 PR3 合并或本轮独立进展。v3 完成了纯范围适配：全部原断言留 facts，完整 reason() 输出原样另存；传递公理与来源留 ontology 视图，派生类型留事实视图。真实 Validator 的全部命名形状目标、两项违规、路径 / 来源约束及修复重验在源码 / 包内相同。一个 constraintDefinitionId 将承载完整保存模板图的契约草案未被本模块擅自变成多定义协议；实际 Store、授权、引用、选中 resultId 与版本绑定仍待 I03/I04。

I03 所需的新内部细码来源已交总控，未直接改公共分类。新 fresh 模式每个子进程不先执行 S1 measure / suite / shapes parse，完整首份结果 flush 后再执行 warm；原 v2 FirstAfterS1 / startup 数据未改写。35 份新证据保留全部原值、stderr、版本、依赖 / 许可 / 动态链接 / 原始日志 / 哈希；系统负载与 OS 缓存未控制，测量波动不解释为确定提升，也没有容量通过线。

正式下一步保持原目标：实际 I03 冻结 / 双审合并和 I04 真实任务基线就绪后，刷新 develop、完成任务 / 持久化 / 取消 / 错误 / 包内 / 窗口原验收，再创建两个指定模型的新全范围审查并逐项处置。没有批准操作当前桌面，无 stub、提前能力注册、push、PR、CI 或合并。
