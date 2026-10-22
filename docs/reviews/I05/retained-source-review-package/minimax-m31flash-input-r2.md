# I05 完整保留源码独立只读审查任务

你是唯一独立审查者之一。此次为补齐此前未通过指定双审的全部保留工程范围，不是仅看22模块或新70测试函数。不要读取另一位本轮审查者的prompt、过程、报告或结论；只读共同固定输入和本人报告。不要自建Goal，不提交/切分支/push/PR/merge，不修改任何旧实现/测试/依赖/配置/验收、原件或黄金。

## 精确任务身份

本人唯一 workspace：/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-retained-review-minimax
这是独立普通物理 wrapper，无 .git，实际 branch=N/A。固定 packet candidate SHA 由 root 在派发前以 dispatch receipt 精确绑定；本人核 instructions/own-input-manifest.json 和输入收据，禁止从目录名猜 SHA。
唯一可写 reports/、scratch/、review-status/；本人完整报告 reports/minimax-m31flash-r2.md，任务设置/终态读回 review-status/minimax-m31flash-r2.json。根 AGENTS.md、instructions/、immutable/、data/ 全部只读。
产品批准 base 5f910b52c69d86a1076b2032e5d3c63e715947f3；完整 source-only 候选 2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64；最终过程 61f53dbe76262f5003065900a4e97d9a6130014b，仅六 docs delta。原产品和供方树 STOP，不修改、不混合执行。
先读 instructions/receiver-guide-r2.md、immutable/current-policy-addendum-r2.md、immutable/current-policy-addendum.md、immutable/r2-guidance/ 四份现行规则、immutable/coverage-matrix.md/json、immutable/input-manifest.json、immutable/author-validation.json、immutable/candidate.patch.json 及 immutable/reference-diffs/。固定 archive 为 immutable/frozen-inputs.tar.gz；安全只读展开位于 data/snapshots/，保持各版本 namespace 分离。所有原件映射的 archiveMember 均加 data/ 前缀即可定位本人的完整普通路径。先核真实输入 SHA/manifest/receipt，再按完整 base→2cf 范围审查。

## 全部原需求和固定范围

frozen-inputs.tar.gz snapshots/main-source-only/ 为2cf整个Git树；snapshots/main-completion-process/为61f六docs。主树中 docs/prd/PRD-本体学习与落地Agent工作台.md 的原FR/附录C–G、第10–12节与57P0、docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md 的S1/S2/S3/C1/B1/U1全文、ADR-0001与I01 ADR-0002、M0清单均保留。不得缩减原验收。
reference-C4/docs/reviews/I05/inputs-c1/七件、round-1/full-review-input.md、round-2/full-review-input.md、round-3/full-review-input.md和I05 acceptance/status/Q6差异表保留原I05 launch/resume/Goal原要求及精确原suffix；操作政策以当前guidance覆盖旧静默限制，不倒改历史冻结字节。
主source-only根收口见immutable/guidance/I05-source-package-source-only-root-closure.md；主 docs/reviews/I05/source-package-probe-source/ 的R1 Fail、R1处置、R2限定静态Pass、最终delivery及全部manifest/readback/首失败都须读。源码阶段没有runtime，不能从“70函数/417观察定义存在”推通过。
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

## 本轮物理隔离和自动状态读面

仅访问本提示给定的本人 workspace。不可读取或发现任何兄弟目录、其他本轮任务的 prompt、过程、报告、任务状态、应用自动状态；不得用搜索、Git worktree inventory、工具全局任务发现、全局应用状态目录或跨目录扫描间接取得。若需核产品 Git，仅允许明确固定 ref/path/blob 的读取，不扫描其他 checkout。独立历史 C1 两份报告及终态属于共同冻结必读输入，不受本轮 peer 禁读误遮。

只读 immutable/、data/、instructions/ 及根 AGENTS.md。只写本人的 reports/、scratch/、review-status/，其中 review-status/application-metadata/ 当前为空；应用未来生成元数据时，只能在 root 实际确认属于当前任务且批准的本人路径内读写。应用若要求全局状态目录，不自行扫描或扩大范围，交 root 获取当前任务的精确读回。当前空 baseline 不代表应用 metadata growth 已实测。禁止 symlink escape、跨根 hardlink、共享可变 .git、scratch 或报告。data 内部只读 hardlink 指向本人数据，禁止编辑或 chmod。

若意外看到其他本轮任务内容或范围外 metadata，立即停止本轮审查，不继续搜索或读取，不删除已有真实事件；仅保存已经实际观察到的最小事件及时间、来源、路径类别，在本人报告告知 root，由 root 判定独立性及是否重开任务。不得借意外发现继续读 peer 或自行宣称无污染。

实际创建来源、任务原生 ID、本人模型/thinking/逐任务权限、实际 workspace 路径、根内输入 SHA、本人 prompt SHA 均由 root 真实读回后记录。wrapper 是独立普通目录，无 .git，branch=N/A；不要创建 .git 或把备包分支误认成本人的实际 branch。未有任务时 ID=null、settingsReadback=pending，禁止把本提示要求当已经达到的设置。

## 本任务专属设置与输出

指定 M3.1-Flash，thinking=xhigh，逐任务权限=permissionMode=bypassPermissions。这是待真实读回的要求，不是已派发记录。仅写本人 reports/minimax-m31flash-r2.md 与本人必要结构收据。原生 ID 不可见时写 unknown 并列可定位标题，association 标签另列；默认配置不证明逐任务设置。实际任务当前 0、设置读回 pending、应用自动 metadata growth 未实测，不沿用其他任务身份。完整原验收、所有原 Fail 与运行缺证仍须在最终结论逐项交代。

# R2 原件精确映射

活跃M0原件为主2cf的I01 inputs版本；I03 inputs副本逐字相同。历史I05必须读实际round1、round2、round3全文及inputs-c1七件，另读C1双报告与终态。不存在的旧round4指路不延用。每一行均核固定Git/blob/bytes/SHA与原bundle清单，无需重解包。

| archive member                                                                                | ref                                      | bytes | SHA256                                                           |
| --------------------------------------------------------------------------------------------- | ---------------------------------------- | ----: | ---------------------------------------------------------------- |
| snapshots/main-source-only/docs/prd/PRD-本体学习与落地Agent工作台.md                          | 2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64 | 93584 | 7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb |
| snapshots/main-source-only/docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md | 2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64 | 35812 | c289a1cd1a9cf40187ef6e506e134b0edcae6dea95d9e99805d4f3045e67cf96 |
| snapshots/main-source-only/docs/reviews/I03/inputs/m0-review-and-update-plan-2026-10-19.md    | 2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64 | 35812 | c289a1cd1a9cf40187ef6e506e134b0edcae6dea95d9e99805d4f3045e67cf96 |
| snapshots/main-source-only/docs/architecture/0001-desktop-framework.md                        | 2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64 |  3876 | 6a7f9448df6815929c589dee0f322c02af9dfda28d68e73769ac5ec028107463 |
| snapshots/main-source-only/docs/iterations/I01/ADR-0002-storage.md                            | 2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64 | 13747 | dc6e76ee9c46ac4b2b760c0bfcc2263e7c3b602386afbc896392c06e0a32fc30 |
| snapshots/main-source-only/docs/m0-checklist.md                                               | 2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64 |  2318 | 72ed4421a2704ce0bb01488fcfb3a8e5ae8f1b0783f65000554df343c2221070 |
| snapshots/reference-C4/docs/reviews/I05/round-1/full-review-input.md                          | 523c478d5f39671c4ac7c1ea6997e51d3047d58e | 40684 | a3ccbc7b4e01ad704dab1c1263c0974c120db929f3bec02b6aa0111d5b3ceaf3 |
| snapshots/reference-C4/docs/reviews/I05/round-2/full-review-input.md                          | 523c478d5f39671c4ac7c1ea6997e51d3047d58e | 43830 | 5b703834fcf77c72f76b67b9ad10f392af1b18f2ed30c1dfa0fd317f34e09887 |
| snapshots/reference-C4/docs/reviews/I05/round-3/full-review-input.md                          | 523c478d5f39671c4ac7c1ea6997e51d3047d58e | 43945 | 35559cda9f401a6fd58ab5551d37d1d18dc5a44bbcd2cc8ce521c3fbaa0c85e6 |
| snapshots/reference-C4/docs/reviews/I05/inputs-c1/I05-launch-prompt.md                        | 523c478d5f39671c4ac7c1ea6997e51d3047d58e |  5918 | 3204dbc196151d0523e1c2f9ea487838011203acbeb58dfc8eb87ddfe553520c |
| snapshots/reference-C4/docs/reviews/I05/inputs-c1/I05-resume-integrated-I04-20261021.md       | 523c478d5f39671c4ac7c1ea6997e51d3047d58e | 11084 | d59b903d3dbb7b85bd5edf61a25a7428a1b69e33def71165e89d292a1ec89323 |
| snapshots/reference-C4/docs/reviews/I05/inputs-c1/goal-objective.md                           | 523c478d5f39671c4ac7c1ea6997e51d3047d58e | 16870 | d1e4993b5c0ecfe83594f77186ab9e03374dfa90231c5d1778004b508d5c825d |
| snapshots/reference-C4/docs/reviews/I05/inputs-c1/parallel-coordination.md                    | 523c478d5f39671c4ac7c1ea6997e51d3047d58e |  8434 | cc066acf21efea5ce91f3348d532002fc3b007468f295666e61c8fd71fb78acb |
| snapshots/reference-C4/docs/reviews/I05/inputs-c1/policy.md                                   | 523c478d5f39671c4ac7c1ea6997e51d3047d58e |  3357 | 1915bf751ed663744420595275565ddef6676e7d0806aa8c8c1d38d06656f716 |
| snapshots/reference-C4/docs/reviews/I05/inputs-c1/scope.md                                    | 523c478d5f39671c4ac7c1ea6997e51d3047d58e | 14266 | 853162d9d9dceea3e66db64229ecab5aa703223f0bd86b40827b5b5e60cc2f99 |
| snapshots/reference-C4/docs/reviews/I05/inputs-c1/sources.json                                | 523c478d5f39671c4ac7c1ea6997e51d3047d58e |  1954 | 05b1af026b7c2c3705f915c44201f3933e5ee44d5265aeee8ec3a2823e5dd968 |
| snapshots/reference-C4/docs/reviews/I05/round-1/zcode-glm53.md                                | 523c478d5f39671c4ac7c1ea6997e51d3047d58e | 25625 | 9b34bb72eaeb35826434448ef84e205cbda865d769402c62200f28982aed8b31 |
| snapshots/reference-C4/docs/reviews/I05/round-1/minimax-m31flash.md                           | 523c478d5f39671c4ac7c1ea6997e51d3047d58e | 93217 | 62001ba637de4937d78f8f07c50982155940817041961259481298e5348a998b |
| snapshots/reference-C4/docs/reviews/I05/round-1/observed-terminals.json                       | 523c478d5f39671c4ac7c1ea6997e51d3047d58e |  3245 | d316bff606ee7e3b4efdad29bd96995621694904ff1303e70dc6084ba0eff8b6 |

shape a15 相对43d 的143项过程原件在 immutable/shape-process-map-r2.json 显式映射到四现存 integer/date namespace，逐路径/blob/bytes/SHA 相同；不是新缺包，也不代表其结论可以替代本次独审。
