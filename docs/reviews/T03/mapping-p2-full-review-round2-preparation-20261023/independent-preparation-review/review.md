# Mapping P2 R2 实际准备包独立静态审查

结论：**当前准备包静态接受，未发现必须先修改 fullinput 的阻断。** 两份实际 fullinput 均已全文读至 EOF，ownroot 副本、固定历史、1028/173→180 集合及可写边界能够对应。这里只接受“准备完成后交 root 决定 START”的输入准备状态；不签产品审查 Pass、实际任务受理、模型设置、完整双方 Pass 或运行验收。真实投递前的本方 operator UI 收据仍待 owner 提供精确 bytes/SHA；现在两处实际不存在，实际身份/后台字段保持 UNKNOWN，不能从旧 SID 或 prepared 请求填入。

审查者不是本包 scope 或 prompt 作者。只在本目录写独占审计脚本、双流、证据与报告；未改 source、测试、模板、输入、其他报告或配置，未 commit。没有候选导入、产品/测试/安装/toolchain 执行，没有 CUA、建任务、平台 API、native 或受限载荷读取；没有进入 STOP 树或另一方 R2 运行资料。

## 固定输入与全文读取

受审 manager 为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping-p2-boundaries`，观察 HEAD `2417110d071a3c62b781e2909bdcb0a62baea2db`。新包当时未提交，实际两个 review root 都仍是 detached `c1e44f81723f9c616f669f56481d1b1ada7e57f2`，产品 `da1795b20c3c0d47ae975fe3371e802092a4b429`，原证据 `4ec492f07d261164283a939c65b5e835c30e561e`。批准 base `5f910b52c69d86a1076b2032e5d3c63e715947f3` 与 repairbase `30319412daf8ae4745987babf7bbed93c53b6b42` 分列，不混作批准起点。

| 实际完整输入 | bytes | SHA-256 | 全文读取 |
| --- | ---: | --- | --- |
| mapping-P2-zcode-round-2-full-input.md | 66551 | cb63ac1a0b10ebb74b8031600208624aea5e605f509d99ab2866f397f382adda | 1–126、127–260、261–413 EOF |
| mapping-P2-minimax-round-2-full-input.md | 82586 | 99d487cafed02acf7701a07565e02cf717fa7c4eb172d62fc87457dae6b7bacf | 1–170、171–330、331–524 EOF |

不是只读模板或头部。尾附上一轮 44835B / 44876B 的完整输入均在上述全文范围内。分段实际工具结果标识保存在 read-record.json；该记录是本会话读回记录，不冒原始 stdout 备份。之后又读回当前控制、范围、17 样例、写面和尾附关键段以核冲突。

两个 ownroot 分别为 `.worktrees/T03-mapping-P2-zcode-review-da1795` 和 `.worktrees/T03-mapping-P2-minimax-review-da1795`。每方 `build/review-session/round-2/input/<本角色fullinput>` 与 manager 原件逐字节相同。两个 manifest 均为 **24 个成员加自身**，实际目录文件集合正好匹配，没有另一方填充的新 prompt 或 actual runtime 状态。每一成员实际 bytes/SHA 对 manifest 成立；manifest 自身明确 excluded，外部 dispatch-index 再绑定其身份，因此没有把自身 hash 写进自身的循环。

Z manifest：4522B / a92d61703af35fa023464fda55a8382ed3af89b4bdf13dcc720935dbc6b8a79b。
M manifest：4526B / 0b225171f795927fc786133bf6eeeb111ca7091e68390ad810c14d394e5f6dc4。

Z 旧附录从 byte offset 21716 起至 EOF，M 从 37710 起至 EOF；独立与固定 241711 的 dispatch-v2 原件比较，相等，SHA 分别为 8106610dac75122b6846c8050e5352f51bd90319179dee838c26ffc372fc1abf / 48839f37ed03a220ea1f82cf97e67528a4a82fd7f0ee769be47b213e55288662。旧原字节未被格式化或替换。

## 范围没有缩减

独立以 `git ls-tree -rlz c1e44…` 对实际 1028 项 mode/type/blob/bytes 与 full index 逐项核对，通过；索引 SHA 为 a8afd3637dcc7fb613c95bd3009d20294e815a96b2043ed108a67afdef673eb4。这里只证明身份和准备导航，不是审查者已完成 1028 项产品语义审读。

从固定 legacy mapping-S1-fixed-inputs 重新取原 866 路径和 173 engineering，再与当前 index 对集合：866 全保；173 工程全保，171 原 blob 未变，两项变化确为 mapping/probe.py 与 test_mapping_entrypoint.py；新增 7 项真实 docs 工具/配置；零删除、零重分类。非 docs 138 保持，docs 工程 35→42。新增七项为：

- mapping-p2-boundaries-20261023/independent-review/audit.py；
- mapping-p2-boundaries-20261023/verify-packaged-boundaries.py；
- mapping-p2-dual-review-preparation-20261023/.gitattributes；
- 同目录 owner/freeze-scope.py、owner/make-dispatch.py、owner/prepare-environment.py；
- 同目录 p2-original-raw/build/mapping-p2-boundaries-20261023/run-command.py。

以上七项均在 `docs/reviews/T03/` 下，不能以 docs 或扩展名排除。完整逐项身份在 static-evidence.json 与原映射中。180 项 engineering-eof-tasks 正好覆盖当前工程集合；独立读取固定 Git blob 计算 bytes/SHA/行数，AGENTS 则用实际受保护覆盖，180 项有效导航全匹配。状态仍 NOT_STARTED，行数与 EOF 目标没有冒语义完成证据。

以 4ec 的 Git 路径集合找出原 866 中当时缺的 11 份 T03 文档，当前 11 份 mode/type/blob/bytes 均精确等于原 legacy 身份，不只依据作者“已恢复”字段。完整名称记录在 static-scope-extra.json。包括两个 archive stderr、ignored-artifact-archive/root-artifact-recovery，以及 round-1 的 evidence-index、两 prompt、preparation-checks/manifest、scope-and-evidence/identities。

Z 导航保留全部 15 unit 候选与 5 e2e，集合由当前 index 独立得出，未因自报 14 猜删一项；具体额外哪项上轮已全文仍 UNKNOWN。18 个 explicit partial/结构/身份级项保留；旧 docs 工程 35 扣明确全文的 `docs/iterations/T03/verify-packaged-probe.py` 后 34 项均保留，不从“约25”猜删其余9。M 的 153 项与固定上一轮台账的原 rows（含空 note）逐字段完全相同，级别仍 144 METADATA / 8 PARTIAL / 1 UNREAD；原 27 FULL 不因此免除本轮重读。

PRD 的固定原件 93584B / 1255 行 / SHA7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb 可达；M0 原件 35812B / 207 行 / SHAc289a1cd1a9cf40187ef6e506e134b0edcae6dea95d9e99805d4f3045e67cf96 可达。输入正文保全 59FR、57P0（55精确+2注释）、2P1、附录C–G、§10–12、M-01–06/G.1、待决Q、M0六节S1/S2/S3/C1/B1/U1、原副本、ADRs、requirements/50acceptance/plan/review/交接，以及原19入口/866历史阶段/首败与HOLD/UNKNOWN。这是输入范围接受，不代替新模型逐条完整需求审查。

## 历史引用与当前控制一致

潜在“848 历史 raw 全部强制重读”问题已直接检查原 JSON：848 行恰好覆盖当前 documentation_or_evidence 集合，每行 `round2ReadRequirement` 为 **Full allowed content/structured semantics or exact authorized exception**，没有工程导航的 requiredReadThrough/requiredStartLine 或 `FULL_NEW_SEMANTIC_REVIEW` 字段。正文第38行、88行及交付段明确允许已核封存原件按原阶段和真实读取方式引用，不得涂成新 FULL，也不免除全部180工程、完整需求和29项的本轮语义判断。故当前未形成这一阻断。

18 explicit partial 中9项文档被明确要求新读：4份ADR/架构文档、4份控制快照、coverage-matrix。它们是点名的需求/控制缺口，并非848全部重复raw强制新读。应执行当前这一区分，不用哈希工作挤掉真正工程、tests和需求。

6份 history 副本逐件等于固定241711的 Git 原件：两 completed 全报告、29台账、独立收件审查、owner处置、closure；没有改结论或级别。完整29唯一编号正好为Z1–Z7/F01–F11/Obs-1–Obs-4/N01–N07。新正文要求新模型读两报告、29原文/处置后回到固定源码/原件独立判断，不把 owner 处置当预设正确答案；不造“原15问题”新门。

最新 root 对两份 completed 报告/29台账共用为上一轮历史的授权，在两份新正文显式覆盖旧 combined-not-forwarded 时态限制。旧 NotPass、Z局部Pass、覆盖不足、完整双Pass=0保留。禁止对象仍是 **R2 peer 新 prompt、身份、进度、报告/raw/metadata**，而不是隐藏已完成历史。历史文件里的旧另一root路径仅为历史引用，当前规则禁止追去搜现场。

| 旧附录可能误导的内容 | 新正文约束及判断 |
| --- | --- |
| 旧 root/branch、旧报告及 task-actual 写面 | 当前唯一 ownroot 与 round-2 普通写面明确列出；旧 task-actual、旧报告/raw 和 operator-* 全只读；可操作 |
| 旧 prepared/身份与旧 GUI/T08 时态 | 请求与实际分离，旧SID不续，当前无lease/无CUA；实际字段UNKNOWN/null，不继承旧状态 |
| 旧“已安装/fresh”、environment.sh | 仅复用本方原有实体，旧 setup 只读，不source/重装，不声称新fresh |
| 旧303 Pass、旧638/1110或其他阅读数 | 当前候选/产品/证据分列；原303历史不能替代c1e44完整新审，1116/mapping专项边界保留 |
| 旧依赖首次导入概括 | N01明确局部from不等首次初始化，允许本方明确普通已装源码静查、不import；实际历史首次时刻UNKNOWN，不反向泛化全部guard前 |
| 旧宽metadata写面或桌面恢复说明 | 当前本轮唯一写面与无运行/CUA票优先；静态工具拒绝保留，不换工具绕过 |

固定P2 oracle与actual receipt中17 ID集合相同，6新增+11旧项明确，allCaseRecords 的逐case独立exit仍null。正文保74原raw、440inventory、三模块PYZ/source仅co_filename归一化/optimize0、三额外参数拒绝与-O；原P2树一次source/一次package外层退出及三socket API固定构造/解析域累计计数边界准确保留。B2已知坐标、四CSV真实issue定位、Obs-3最后解析case快照与JSON排序非执行顺序均列为需核争议。未重读或重跑全部raw/PYZ载荷，没有将准备核验升级为新运行证明。

## 现场、路径及待投递条件

两自身树当前 `git status --porcelain` 都只有 ` M AGENTS.md`，实际AGENTS15147B且精确等于manager覆盖。两 `.venv` 与两个 node_modules 均为本树实体目录，lstat 非symlink、对应顶层 inode 不同；旧setup-receipt 的 bytes/SHA与准备readback一致。未做新的全环境 inode扫描或运行隔离证明；共享基础Python只读symlink仍按旧披露，不能把本次元数据核验称fresh重建。

每方 round-2 的 input/reports/raw/scratch/tmp/metadata 目录都存在；文件入口和 history/source refs 可达。本轮模板/生成器作为额外过程源码在各自 input/preparation-tools，非对方填充新prompt；完整index、180导航、scope和历史副本均封在 own input 内，无需跨去另一root取新意见。

dispatch 与 own prepared-request 中 sessionId/turnId/actualSettings/GUILease 均null，accepted=false、PREPARED_NO_ACTUAL_TASK。当前两处 `metadata/operator-own-ui-pre-submit.json` 实际不存在；仅查其存在性，未读取任何本轮 peer runtime资料。模型可以如实记录UNKNOWN，这不阻断当前“准备”状态，但 **正式投递前 owner 仍须按真实GUI START来源提供各自新UIreceipt及精确身份**；不能据本报告把这一尚未发生的步骤记为已完成或把请求设置记为实际。

绝对STOP、caller WIP、SDK/witness/descriptor/index受限载荷、私有I05build/CLI/native边界未因完整审查扩大。普通工程、tests、fixtures、锁与工具仍需新静态语义，不把受限payload例外扩大成普通源码免读。

## 独立核验过程与限制

独立脚本均为 `.py.raw`，只用标准库及只读Git/text/stat，不导入候选。首次 static-audit.py.raw 因我把 dispatch 的嵌套 `inputManifestIdentity` 键误写为平键，在内部核验处 KeyError，exit1；原源码与原始双流保留，非包缺陷、未生成成功结论。另写 static-audit-v2.py.raw 更正实际键和 appendix.offset，exit0，31个检查全通过。附加 static-scope-extra.py.raw exit0，11个检查通过。两份 stdout/stderr 均直接重定向保留，首次错误未覆盖。

JSON/哈希/行数/静态路径检查证明的是准备输入一致与可定位，不是产品语义Pass、运行通过、性能、独立完整双审或生产发布。没有执行 npm/uv/pytest/ruff/pack/engine/e2e/GUI/native；无未变更check/pack重跑，无task创建。本报告不补旧runtime、旧收据、旧模型覆盖或新增本轮意见。
