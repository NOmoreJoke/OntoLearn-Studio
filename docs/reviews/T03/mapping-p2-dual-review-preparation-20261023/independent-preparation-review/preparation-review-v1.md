# Mapping P2 新双外审包独立准备审查：首包 70f432

结论：首包 `70f4323fd574d7955fcbf7e581b2d06dd1f10e1c` **存在一项派发前须修正的 P2 定位缺口（R1）**。完整输入、需求、历史及执行边界没有发现实质缩减；两新树和独立 setup 身份成立。但固定 c1e44 审查树内没有后生成的完整 candidate 索引，首提示未给出审查方可用的固定定位。首包不宜直接派发为“完整材料已可取得”。这不是产品审查，也不判产品双 Pass。后续 v2 修订须另写 delta，本报告保持首包原结论。

## 固定对象与方法

主控树为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping-p2-boundaries`。本审查的过程包固定为 70f432，实际受审工程 HEAD 为 `c1e44f81723f9c616f669f56481d1b1ada7e57f2`；产品为 `da1795b20c3c0d47ae975fe3371e802092a4b429`，证据源为 `4ec492f07d261164283a939c65b5e835c30e561e`，批准 base 为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`，repair base 为 `30319412daf8ae4745987babf7bbed93c53b6b42`。这些角色没有互相替代。

只做静态文本、JSON/CSV 结构、Git metadata 与受授权普通证据字节/哈希核对；依赖隔离只 lstat inode，不读安装二进制载荷。未运行产品、安装、check、pack、GUI、mock 或任何 owner driver；没有访问 STOP 现场、SDK 或受限 witness/descriptor/index payload。本 agent 只写本独占目录。PRD/M0/全工程在本任务中的核对是身份、完整范围清单及相关标题/数量核对，不冒充对 1028 载荷或全 PRD 的产品语义外审。

`audit-v1.py` 是本 agent 的独立静态核对脚本，`audit-v1.stdout.json` 是实际执行输出，stderr 为空，exit0。脚本固定从 70f432 取包，从 c1e44 取候选 metadata，并只对两个明确审查树读当前状态/安装元数据。无需也没有执行准备包自带的 setup/freeze/make-dispatch 工具。

## R1 / P2：完整 candidate 索引在审查现场不可定位

两新树实际都为 detached c1e44，且 README/历史材料在树中。但路径 `docs/reviews/T03/mapping-p2-dual-review-preparation-20261023/dispatch/full-candidate-tree.json` 在两树均不存在；该 dispatch 在 c1e44 固定后生成，70f432 仅固定其主控侧过程文件，未改变两树 HEAD。

首提示称“独立派发包中的完整 candidate tree 索引绑定此 HEAD”，没有指向主控固定 70f432 Git 地址或自身 metadata 的绝对地址/身份。首 `owner/make-dispatch.py` 只复制 prompt 和 task-actual 到各自 metadata，没有复制 1028 项索引。故模型按本树相对包目录寻址会缺失此输入；不应依赖它猜路径、扫描别树或自行重建一个清单来弥补发审定位承诺。

最小修订：保持两树 c1e44 不变，把原字节完整清单复制到各自受允许 metadata，header 明确自身绝对路径和 SHA；如需 dispatch-index/新工具源码，也在同一写面提供固定身份。另一可行方式是明确只读 Git show 的独立 packet commit:path。无需新产品、安装、check 或 pack。本问题已先报主控，主控确认成立；本首报告不提前追认其 v2。

## 完整输入及需求范围核对

- 原 mapping fixed manifest 的 **866 条** metadata 与原 process `3c396070c74fbf09cf319b0230c6f96ed2858482` 逐项相符；完整原 866 路径在 c1e44 均存在。原 **173 工程条目包含 35 份 docs 工具**，这 173 路径的 product→review HEAD metadata 全等；所有 non-docs 工程也全等。没有把 naive 138 当作完整工程 173。
- 缺失的 **11 份历史文档**已恢复，各自 current Git blob 与原 process 精确相同。原 866 中现行文档的后继差异保留独立身份；旧版本仍按原固定 ref 读取，没有用新文档覆盖其历史语义。
- c1e44 完整清单 **1028 项**与真实 `git ls-tree -rlz` 逐字段/路径集合完全相等；blob OID、size、mode、kind 只作身份元数据，不是已经全文阅读载荷的证据。
- `input-copy-provenance.json` 的 **34 份**副本，bytes/SHA 全符；有 sourceGit 的项目与指定原 Git 字节全等。完整 ed9 共享包/原 19 入口、历史 inventory/coverage matrix、原失败/验收/缺证仍列为必读，并未缩成两个产品 delta。
- PRD 为 **93584 B、1255 行、SHA `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb`**；完整 requirements.csv 实际 59 行，P0 前缀 57（55 精确 P0 + 2 带注释 P0），另 2 P1；acceptance-baselines 为 50 行。首提示要求全篇、附录 C–G、§10–12、原延期/待决项及父 P0 门，FR-300–304 只是定位。没有把完整专业模式/模型增强注释错误删出 P0 范围。
- M0 原输入为 **35812 B、207 行、SHA `c289a1cd1a9cf40187ef6e506e134b0edcae6dea95d9e99805d4f3045e67cf96`**。S1/S2/S3/C1/B1/U1 全六节及 I03 副本、m0-checklist/ADR 都在必读范围。M-01–M-06 纠正为 G.1，旧提示误称 D.1 不再作为新范围定义。
- `.gitattributes` 仅位于新包目录，内容为 `** -text` 并说明保护原 CRLF；34 副本对冻结 Git 的原字节核对成立，未更改产品工程。首次 CRLF stage 警告和 138/173 误计已在 preflightCorrections 明列，最终记录不再沿用错误口径。没有为清理格式而改写 raw、旧提示或原 CSV。

## 历史 18 编号与 P2 实际包边界

历史 JSON 的 ID 集精确为 Z1–Z7、F01–F11，共 18；对应三份原报告/主控草案 bytes/SHA 全符，history manifest 的 8 个文件亦全符。索引将原严重度、原报告、主控技术处置和未验边界分列；F05/F06 为验证观察，旧 P1/P2 为证据登记 ID。README 与新提示明确没有已核的“原 15 问题”，未伪造 15 条新门。

新提示要求完整复核全部 18 项，包括 Z1 preview 残余说法、Z2“维持 P3/终段无 P3”的报告矛盾、F06 普通 XML 样例不能证明 CDATA 普遍结论、F09 总 1110 已含 mapping58。主控草案不作新模型结论，新六项不会自动关闭其他 UI/公共写入/继承问题。此准备审查确认其分层与可追溯性，不代替指定模型重新判这 18 项。

P2 receipt/expected 均实际列 17 case，新增 boundary 集恰为 6：外部 cached formula、外部 hyperlink、CSV 文件/列/单格/行四种限额定位；三模块 codeBinding、440 项 inventory 与 74 原件范围均有明确入口。74 relocations 的每份副本及对应原 P2 build 原件实际 bytes/SHA 全符。原记录 cwd/时间/argv 保持，不冒充新审查树运行。

提示准确保留：17 项共用 source/package 各一次外层 exit，逐 case independent exit 为 null；socket 仅三 API 在固定构造/解析阶段的累计计数，dependency import 在 guard 前；成功引用样例 column2 是已知 B2 坐标，只有四 CSV 是实际 issue 的完整定位；probe/source/plan 的 co_filename-only source/PYZ 比较不能扩大到全部依赖语义。实际既存包/check 是原 P2 候选历史证据，不能写成新树 fresh 包或产品父门通过。完整旧 11 项 oracle/输出保留，原 303 Pass 不继承。

## 两树、setup 与提示真实性

两新树分别为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping-P2-zcode-review-da1795` 和 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping-P2-minimax-review-da1795`。独立读回两者均 detached c1e44，唯一受跟踪工作区差异是 unstaged AGENTS；两份 AGENTS 均 15147 B / SHA `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`。

两树各三条 setup 记录均 exit0：npm ci --ignore-scripts、指定自身环境的 uv sync --frozen/--link-mode copy、Electron installer。六条收据的原 stdout/stderr 字节和 hash 均相符，开始 HEAD 为 4ec，之后只追加文档，没有声称在后生成 c1e44 上重新安装。两树 node_modules/.venv 是实体目录；各自普通文件 inode 为 16095，独立 lstat 得两集合交集为 **0**。共享基础 Python 只读解释器 symlink 已披露。这仅证明安装与元数据隔离，不证明 check/pack/GUI 或运行验收。

首 Z prompt 43671 B / SHA `ef4e8693f367e563cbb95df46f6593b508d490684866611c9188abaf06581cf0`；首 M prompt 43708 B / SHA `e8a3bf8843379a1ff6051a419b7492aa112cd9624be4563afd6c127ccb35013a`。两者 header 仅角色、请求设置、自己树/报告/metadata 地址不同，其余新完整范围及执行限制相同。append 三份 policy 的 offset/bytes/hash 与原快照全等，legacy suffix 与 3df399 原 Git 字节全等。三份 policy 快照与本任务对应当前控制原件实际相同。

模型/思考/权限是请求值；task/session/turn/actualSettings/lease/terminalOutcome 保持 null，状态为准备排队，不伪装真实任务。历史共同规则及旧 prompt 的旧树/建 Goal/旧状态由新头明确覆盖；现行静态限制优先，禁止自行产品命令、安装、owner setup driver、pack/check、GUI 或私有 provenance build/CLI，T08 GUI 资源无 lease。历史两报告已封存可读，与禁止互读对方本轮意见/进度/raw/metadata 明确区分。

本 agent 的 audit-v1 运行期间，主控已开始 v2 修复，自身可变 metadata/dispatch-prompt 与首 70f432 不同，故 stdout 的 ownPromptCopyExact=false 如实保留。这不是首包 70f432 canonical 文件损坏或历史 readback 被推翻；审查时序不同，不用当前 metadata 替换首 readback。首 70f432 prompt 身份及其原 preparation-readback 保持固定；该可变部分将在 v2 delta 单独核对。

## 准备结论的边界

R1 修正前首包不作可用性签收。本次没有发现伪原 15 门、旧 303 Pass 继承、两模型本轮意见混入、工程/PRD/M0 范围缩减或 setup 冒充产品运行的其他准备阻断。该判断不代表产品正确、指定双方通过、父 57 P0、CI/远端、两 OS、GUI/native、安装签名、干净设备或生产验收已完成。实际派发仍须 root 交接 GUI 资源、原 owner 创建真实任务并读回实际设置；准备文件和本独审报告均不能填充这些实际证据。
