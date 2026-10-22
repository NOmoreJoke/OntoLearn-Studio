# Mapping P2：全新完整独立审查（@@ROLE@@）

这是全新指定外审任务，不能继续旧303会话或继承旧Pass。请求设置：**@@MODEL@@**。请求值不是实际值；须在真实任务读回task/session/turn、实际模型/思考/权限和来源。实际ID尚未创建，不能用本提示伪填。审查全程不改实现、测试、依赖、锁、配置、原验收或历史原件，不提交、推送、PR、切分支或创建Goal/其他聊天。

## 唯一工作现场与精确版本

唯一工作树：`@@TREE@@`。实际应为detached HEAD **`@@REVIEW_HEAD@@`**；另一项新审也必须是这个完整HEAD。产品候选`da1795b20c3c0d47ae975fe3371e802092a4b429`，工程/既存证据来源`4ec492f07d261164283a939c65b5e835c30e561e`；批准base **`5f910b52c69d86a1076b2032e5d3c63e715947f3`**，本次两文件修复base另列 **`30319412daf8ae4745987babf7bbed93c53b6b42`**。不能以repairbase替代批准base，也不能以产品SHA替代实际完整HEAD。本轮完整HEAD仅追加文档，与da1795的所有非docs工程（AGENTS保护覆盖另计）逐blob相同。

当前AGENTS保护覆盖15147B / SHA `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`应保持unstaged；Git树内旧AGENTS blob不是覆盖实际值。先核验现场，实际不符则报告具体差异，不自行checkout/reset/fetch/cherry-pick或改文件。所有旧提示、control tasks.json/plan中的owner路径、分支、STOP现场及状态仅为历史来源，不能去旧树运行或借环境，不拼装其他分支互斥代码。

本包目录为`docs/reviews/T03/mapping-p2-dual-review-preparation-20261023/`。同目录README、input-copy-provenance、history-agent和旧完整fixed manifest均需读。独立派发包中的完整candidate tree索引绑定此HEAD；blob OID/清单/数量是身份元数据，不是已经全文阅读载荷的声明。

**完整1028项索引的可用入口**：`@@TREE@@/build/review-session/metadata/full-candidate-tree-c1e44f81.json`，SHA-256 **`@@TREE_INDEX_SHA@@`**。这是owner从同一固定HEAD生成后原字节复制到你自己metadata的文件；不要猜HEAD内不存在的dispatch/full-candidate-tree路径。自己的prepared派发索引在`@@TREE@@/build/review-session/metadata/dispatch-index-v2.prepared.json`，只有请求值/null，不是任何任务实际状态。首版70f432派发定位缺口保留，当前提示是v2修订。

本次索引定位修订的生成工具/模板也在自己`build/review-session/metadata/preparation-tools-v2/`保存原字节副本及manifest，作为额外过程工具源码一并静审；不执行生成器或安装器。实际工程HEAD仍是上述c1e44，不能把这些后加metadata当作已经进入该HEAD或改变产品。历史fixed索引的旧路径仍按其固定Git ref读取，不能去其他树当前WIP。

## 完整审查范围，不能缩成新六项或两个diff

1. **完整工程**：本固定HEAD全部tracked源码、tools、tests、fixtures、配置、锁、公共契约、CSS、构建/CI和docs中的证据工具。继承工程和I01–I04不因owner不同而排除；docs/.py.raw/.input.py.txt/.mjs不能被当散文漏审。两产品delta只是导航。审业务正确性、异常、事务/撤销、来源所有权、历史重放、缓存/草稿/序列化与安全边界；未实测性能不量化。
2. **全部原输入/历史**：原共享包固定ref`ed9cef968b17a1edefc0977b509906fb9f81a336`，原process`3c396070c74fbf09cf319b0230c6f96ed2858482`；同一仓库可用只读Git show精确读取。legacy-fixed-package保存mapping/shared原字节入口；原19文件入口和旧866项完整清单/历史阶段/coverage-matrix继续有效。旧866中11份缺失T03文档已按固定blob恢复，新输入不替代原历史。旧failed/HOLD/UNKNOWN、首次失败、缺证及后继阶段均须保留，不只读最后success。
3. **完整需求与原验收**：全文`docs/prd/PRD-本体学习与落地Agent工作台.md`（1255行、93584B、SHA `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb`）；全部59 FR、57 P0、另2 P1及原延期界限。完整附录C–G、§10–12及全篇其他条款/待决项；M-01–M-06在G.1。FR-300–304是局部定位，不能把其片段当全范围。control-snapshots中完整requirements.csv（57=55精确P0+2带注释P0）、50条acceptance-baselines、plan/review/交接保持原字节。父P0缺口须分别判，不排除后给整体Pass。
4. **M0全文**：`docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md`完整207行及其原I03副本、docs/m0-checklist、ADR/历史输入。S1/S2/S3/C1/B1/U1六节全部覆盖，不能只读入口或摘要。

逐文件记录完整/部分/metadata-only/未读及实际范围、引用证据和未读原因。docstring、定义计数、grep或作者摘要不能冒充全文；大raw/原报告应按允许范围分段读完。JSON/设计结构按完整语义记录，不夸称逐字散文。不能将“其他owner”当免读理由；实际无法完成全范围时明确无法完成验证，不能用局部Pass替代。

## 必须逐项复核的真实历史意见

历史原报告完整保存在`docs/reviews/T03/mapping-followup-1-completed-20261023/`，两个报告均已终态，是此次明确授权的历史输入；不属于对方本轮新审意见。`history-agent/historical-findings-index.{md,json}`提供Z1–Z7与F01–F11 **18个真实编号**的原严重度/性质、原文行、主控处置及未验边界。不存在已确认的“原15问题”清单；根已纠正口误，不能造15条或额外门。18编号也不等于18个缺陷，F05/F06为验证观察，旧P1/P2是证据登记ID而非严重度。

必须独立复核原始代码/证据，不把主控technical-disposition-draft当最终事实或Pass：Z1墓碑preview残余说法与真实分支、Z2重复predicate/reference预检及“维持P3/无P3”矛盾、F06普通XML样例不能证明CDATA普遍结论、F09总1110已含mapping58；其余18项也不能只处置这四项。旧原严重度及改判历史原样保留，报告错误、产品问题、正向观察、继承边界分别记录。未制作/运行CDATA fixture，不虚构已证产品误拒，也不擅改DOCTYPE闸。新六项不会自动修复其他UI/公共接线问题。

## 新P2与实际包证据

首读`docs/reviews/T03/mapping-p2-boundaries-20261023/{delivery.md,actual-receipt.json,candidate-binding.json,fixed-probe-v2-expected.json,oracle-before-run.json,command-records.json,raw-evidence-manifest.json,actual-engine-inventory.json,verify-packaged-boundaries.py}`及其原件。新包的p2-original-raw保存74份原字节副本，raw-relocations只增加定位；原收据中的旧cwd/argv/时间保持，不能写成在当前新树重新运行。

既存实测：fresh check638 TS/1116 Python、sources12、package exit0；真实source和真实新包固定17项完整匹配执行前静态oracle；三额外参数拒绝、source -O均有原双流。旧11项实现/预期保留，六新增为外部cached WEBSERVICE公式、外部hyperlink显示文本、CSV文件/列/单格/行四类上限完整定位。固定caps未改，不接受caller文件或任意URL/script/path。

精确边界：17项共用一次source和一次package进程退出码，`independentPerCaseProcessExit:null`，不能写成17个独立进程。socket是socket.socket/create_connection/getaddrinfo三API在固定输入构造/解析期间的累计计数，dependency import在guard前；不是全OS网络、17个隔离counter或所有公式格式证明。两成功引用case的column2是已知B2坐标，四CSV才是真实issue完整code/sheet/row/column。三模块probe/source/plan源与实际PYZ代码绑定仅归一化co_filename，完整440项inventory是其余实际字节身份，不能升级为全部依赖语义等价。

既存本地Codex独审只作可复核历史材料，不是指定双Pass；本轮须自己读完整源码和实际原件。1116与mapping专项分列，不能沿用“总1110不含mapping58”的旧报告错误。当前实际包来自原P2树，当前新树没有新pack/check结果；不能借旧包运行并伪称本树fresh包。

## 当前资源与允许动作

根已释放I05唯一CPU窗并解除安装暂缓；owner只完成各新树的独立`npm ci --ignore-scripts`、`uv sync --frozen`及Electron installer setup，不是产品验收。安装具体argv/时间/exit/双流、环境路径与基础解释器symlink披露见本树`build/review-session/metadata/setup-receipt.json`和raw/setup-1。node_modules/.venv/缓存属于本树实体目录，不借其他树或共享可变运行库；base Python只读解释器链接如实披露。

**本次新审先做完整静态审读与既存证据复核，不重未变pack/check，不自行安装、更新锁、运行setup脚本、启动Electron/e2e或其他产品命令。** 若某个具体未解问题确需新运行，给owner精确argv/原因/输入/输出和资源条件，由owner按根当前阶段票安排，不向用户重复索桌面时段、不把等待当批准。任何后续运行须新raw轮次保首次失败，不覆盖旧报告/oracle/验收。提示中旧一般“可正常回归”不覆盖此轮具体限制。

GUI目前由T08使用，本提示不证明短lease。静态审查可后台继续，不能自行获取CUA/创建另一任务；原owner仅在根排队交接后真实创建/设置/读回。没有新Goal、付费/API消费、重置或凭据读取授权。

独立写面仅本树`build/review-session/{tmp,scratch,raw,reports,metadata}`及原owner明确的报告路径。完整全文报告：`@@REPORT@@`。实际任务元数据：`@@META@@`。可使用本树environment.sh列明自有路径；不要执行owner setup driver。此轮不产生新的app/build/release运行输出。

## 绝对保留的STOP与独立性

不得读取、扫描、写入、复制、格式化或执行`.worktrees/T03-native-location-N0-build`停止现场（及其caller WIP）；不得研究或调用未签T03-N0 native/producer/caller、局部函数、runner/reader、ABI/loader/drain，不能借票、抬guard或用fixture/dry-run替代。SDK/二进制安装身份/原witness/descriptor/index受限载荷继续按原权限，不因“完整范围”新解码；仅按已固定manifest登记未读/未验。原完整工程源码/历史审读与受限payload门分别记录，不据局部例外删父门。私有provenance真实build/CLI/loader/native另无运行票，不被本mapping票覆盖。

本轮两新任务完全独立：禁止搜索、读取或通过Git新日志/应用数据库/状态库/别的报告取得对方**本轮**意见、进度、raw、metadata；禁止传递本轮意见。已封存历史Z1–Z7/F01–F11按上文同一公开固定包读取，不拿它们冒充对方当前答复。只审本任务，不切旧会话或其他树。模型请求配置和文件存在不能冒充实际设置/完成。

## 必须完整交付

完整报告含真实ID和实际设置来源、精确工作树/HEAD/approved base/repairbase/product/evidence ref、逐文件/历史范围覆盖、实际命令与结果或未运行原因、所有意见严重度/文件行/触发/影响/证据/建议、真实18项逐项处置、六新增/17固定包证据、全部原验收矩阵与未验边界。源码/单元/check/包CLI/GUI/native/两OS/干净设备/签名安装/父57P0/CI与远端/生产分别判，不能仅凭无P0/P1或17项成功给整体Pass。

结论必须明确通过/不通过/无法完成验证及范围；真实任务终态后owner全文读回，不能只阶段摘要、不强改模型不通过。首失败和历史UNKNOWN保持；旧候选双审、本地独审、setup通过都不是本候选指定双Pass。未经同版双明确通过、全部意见处置及必要验收不得push/PR/合并。

下附当前共同规则原文及冻结历史dispatch-v2提示。共同指南中的“建Goal”等新开发通用条款不适用于本既有外审任务；下附旧路径/候选/运行状态以本新头精确覆盖，原需求/历史/安全与发布门不缩减。
