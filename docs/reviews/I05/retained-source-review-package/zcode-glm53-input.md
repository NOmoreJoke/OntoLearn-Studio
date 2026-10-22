# I05 完整保留源码独立只读审查任务

你是唯一独立审查者之一。此次为补齐此前未通过指定双审的全部保留工程范围，不是仅看22模块或新70测试函数。不要读取另一位本轮审查者的prompt、过程、报告或结论；只读共同固定输入和本人报告。不要自建Goal，不提交/切分支/push/PR/merge，不修改任何旧实现/测试/依赖/配置/验收、原件或黄金。

## 精确任务身份

备包树 /Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-retained-source-review-package
备包分支 docs/I05-retained-source-review-package
唯一报告写面 docs/reviews/I05/retained-source-review-package/reports/ 下为你指名的报告及本人纯结构检查收据。
产品批准base 5f910b52c69d86a1076b2032e5d3c63e715947f3。
主source-only候选 2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64。
最终交付过程 61f53dbe76262f5003065900a4e97d9a6130014b，只有六项docs-only delta。
备包candidate提交由总控实际冻结后补充精确SHA；收到任务先核真实SHA和manifest，不把process父/目录名当候选。
原2cf/61f产品树和所有供方树STOP只读；无需也不得切到其它版本来混合执行。

先读 current-policy-addendum.md、guidance/四份现行操作规则、readme、coverage-matrix.md/json、input-manifest.json、author-validation.json、candidate.patch.json及reference-diffs。逐member核bundle/ref/hash；只读完整源码/测试/配置/锁/fixture/资源/许可/首Fail和固定原始证据，按全部base→2cf差异完整审查，不只看R1修复delta。

## 全部原需求和固定范围

frozen-inputs.tar.gz snapshots/main-source-only/ 为2cf整个Git树；snapshots/main-completion-process/为61f六docs。主树中 docs/prd/PRD-本体学习与落地Agent工作台.md 的原FR/附录C–G、第10–12节与57P0、docs/architecture/m0-review-and-update-plan-2026-10-19.md 的S1/S2/S3/C1/B1/U1全文、ADR-0001与I01 ADR-0002、M0清单均保留。不得缩减原验收。
reference-C4/docs/reviews/I05/inputs-c1/、round-4/full-review-input.md和I05 acceptance/status/Q6差异表保留原I05 launch/resume/Goal原要求及精确原suffix；操作政策以当前guidance覆盖旧静默限制，不倒改历史冻结字节。
主source-only根收口见guidance/I05-source-package-source-only-root-closure.md；主 docs/reviews/I05/source-package-probe-source/ 的R1 Fail、R1处置、R2限定静态Pass、最终delivery及全部manifest/readback/首失败都须读。源码阶段没有runtime，不能从“70函数/417观察定义存在”推通过。
所有历史产品与final process命名空间均完整保留，其对应阶段的主稿、验证、独立内审Fail/修订/最终有限结论、原始双流与首失败必须按coverage/source/ref读取；无证据的项目标unknown，不因总控受限收件替代本人审查。

当前主source-only全部源码包括真实canonical调用编排/phase/error/timeout边界、输入loader/descriptor、同selector source/package路径、query/SHACL、fresh prepare→project、producer→capture→strict→roots、离线guard、完整JSONL/输出限额、generator、两纯输入资产和全部70测试函数；目录中的任何基线代码/公共契约/资源/锁/测试和所有Git差异都在工程审查范围。判断实现、错误分支、边界、篡改/缺字段/错误阶段/完整结果和稳定来源，不以计数或文件存在替代逐项语义。

## 分版本覆盖，禁止互斥版本拼接

2cf仅不可变采用date6891的22Python模块（supplier-adoption逐件固定）与T01四资源。22=6891只指22路径字节，不是采用6891完整工程。coverage矩阵独立SHA核211unique blobs，148delta路径×8阶段明确same/changed/missing：
C4产品3/16/2，测试0/2/16；0475产品12/3/2测试0/0/15；3ef产品13/5/2测试0/0/18；6c1产品15/17/13测试0/1/43；8e8产品21/12/13测试0/1/44；43d产品21/12/13测试0/1/45；91e产品21/12/13测试0/1/46；6891产品22/11/13测试0/1/47。这里的delta same22与supplier22集合不同，不可混淆。
source-only没有的24项I05/quality测试、23项T01测试和27fixtures不能由新70函数覆盖声明代替；task-runtime版本也不同。全部固定参考原件在独立namespace，不整文件抄进主树或冒充已采用。
原worker/protocol/bridge/native/harness/CI/锁与T01供方有互斥版本，必须分别核实际ref/path/hash和限定内审，完整说明受审范围与后继归属。旧C4已退出当前发布候选，但不能据Git祖先关系、日期或missing自行判全部旧源码撤回。原semantic_probe、profile_probe、samples及旧验证工具仍保留，分别在引用候选中审清或列独立后继队列。
未跟踪calculation/lexical/restore-tests只有opaque路径/bytes/SHA，无冻结身份；不作为已冻结产品，待owner明确采用/撤回。fee/D2 WIP不在本次可读范围，不使用actual反推任何规范或golden。

## 原意见和真实门禁

C1真实两任务已经终态，native UUID均未暴露，association标签不可当ID；ZCode最终附新候选修复条件Pass、MiniMax最终NotPass/SHACL B-1-prime。早期MiniMax Pass已被同审者后续NotPass取代。C2/C3/C4实际新任务0，不能继承C1或内审为指定双Pass。
C2词法/orphan/GRAPH，C3 hashseed witness，C4 string身份及后续profile/strict/fullview/DAG/SHACL/整数/date实际改动都必须有精确版本的关闭依据；原Fail/局部Pass不能抹除。来源/预算/生命周期/真实validator报告和旧首失败按原件核，不用作者声明代审查。
R1 source-only两P2一P3已由作者修订和R2静态核，仍由你独立确认，不把R2静态Pass当指定或runtime通过。

## 当前可执行边界

当前任务只授权完整工程源码审查与Git、读取、opaque hash、stdlib JSON/tar/AST等纯结构核验；必要检查只写本人reports前缀，记录argv/cwd/exit/完整分离双流/未验边界。不import/执行任何产品、probe、generator、测试或模型函数，不运行pytest/npm/check/build/package/安装/网络/DB/GUI/native/HMR/凭据/417运行；不触碰SQLite损坏输入HOLD、未签native caller、自动审批已拒工作或物理H/GC/RSS实验。不要以full access扩大读写/运行scope。
桌面静默偏好已经撤回，应用创建/设置读回由root按短lease处理；旧“等桌面时段/CLI先登录”不是当前限制。但本轮没有产品/native运行票，不能因此代跑。
产品可读范围与可执行验证范围分离：不等父runtime才审源码；源码工程审查现在完整做，运行证据不满足原门时必须准确NotPass/无法完成验证，不删验收求Pass。

## 必须逐项保留的缺证

T03供应锁28440B/86dfe82d952e2c88edcfc5658f488f6e1f0d04b4ec3b1e6f5c5d3bc4f57e8b73尚未采用，主根锁仍5f20999B/d5d027da6628a2f4fc2e73730ce3a5e40d85aebba95188b0d4c3801ebdde949e；pyproject/entrypoint/build-engine四writer不是本轮采用的实际新组合，八distribution未核实。
同selector source/package实际运行、完整417外部独立oracle及全值/首错/费用/准入/发行校核、loader/cache代码指纹、全JSONL/输出cap故障回归、实际许可与父package、S1 snapshotLoad及12snapshot/12B1 fresh、SQLite损坏输入HOLD、whole-H、真实Job/Store原子origin/owned worker/selected/K0..32/Σ/H、两OS/真人/CI/develop远端等仍未关闭。区分“不在本轮可执行范围”“历史有限证据”“当前没有实际运行证据”，不虚称已Fail产品或已Pass。
历史actual只作原实现的待核证据，不能用来生成/修改独立expected；fixture/golden/原明文和版本不改。对未通过项给精确路径、触发、影响、证据、最小建议和下一真实验证条件。

## 报告必须完整

记录实际任务原生ID（不可见写unknown并给可定位标题，标签另列）、创建来源、实际模型/thinking/逐任务permission读回、工作树/分支/真实packet SHA/base/candidate/process、完整范围和manifest/ref/hash核对。记录每项实查/未查/运行未执行及原因，必要命令完整流，全部历史意见逐项closed/open/不适用依据、严重度/位置/触发/影响/证据/建议。
分别给主2cf源码工程、参考保留版本/测试覆盖、完整原验收三个结论，并给明确整体通过/不通过/无法完成验证。局部静态无阻断不能替代完整门通过；关键运行无法验证时不得给无条件Pass。不要把尚无CI作为push前可执行项目，CI在获双Pass等原门后push/PR阶段、正常合并前核验；本任务完全无push授权。
最终报告必须真实终态、全文可读，不仅摘要；不得读取另一审者意见来协同改判。所有意见由原作者/owner按新候选处置，不能在审查中修产品。

## 本任务专属设置与输出

指定 ZCode GLM-5.3，thinking=最高，逐任务权限=permission.mode=yolo。这是待实际UI读回的要求，不是已派发记录。报告只写 reports/zcode-glm53.md 和本人必要纯结构收据；不读另一方报告/任务。原生ID不可见时明确unknown，不捏造UUID；权限不符由root在安全边界修正并实际记录，不以用户级默认配置代任务设置证明。

