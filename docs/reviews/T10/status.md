# T10 导出与迁移

日期：2026-10-21（Asia/Shanghai）。Owner：聊天 `01a15bce-0a94-7870-9694-f100e78f406a`。

- 工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-transfer-export`。
- 分支：`feature/weekly-t10-transfer-export`；核验 base/head：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 启动状态仅 `M AGENTS.md`；保护 SHA：`db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`，不暂存。
- 已建立本功能 Goal，已实际回执总控。原 AGENTS 的架构计划链接在此基线缺失，已读取归档的 `docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md`。

## 责任与下一交付

只新增启动提示授权的 transfer、project-transfer、renderer/transfer、T10 单测/fixture、docs/reviews/T10 与 docs/iterations/T10 路径。不改公共契约、Store、writer、主进程/preload/App、锁、CI 和根调度文件。

当前实施：只读候选包结构/角色/路径/哈希/选项检查、安全纯文本 HTML 报告和独立页面、完整合成输入/预期、恶意样本、必要测试与独立只读内审。内部候选包版本明确未批准，不能进入产品导入或承诺恢复/重跑/重放。

当前阶段：私有包检查、安全报告、页面和主进程报告文件发布服务已验证。T10 Python 60、报告 TS 18、文件发布 TS 43 项通过；最新稳定整仓 check 为 691 项 TS / 1,112 项 Python 与构建全通过。headless Chrome 打开真实文件服务产物，12 组攻击文本及前导 LF 完整，无执行/外联。新增文件服务内审 3 项 P2 实际修复并完整复核通过；前一版两项 P2 历史仍保留。详情见 verification.md、report-file-internal-review.md；正式集成/父功能未关闭。

首个可恢复实现提交：`d3546af3b6fe895957f9626fd4de28bf59dc600a`，后续记录 `a1c76d8a136519455267c00d08f63c68ecea0806`。本轮实现提交 `c3c7e90f721344113c4279d663127f9c8d5bda59`，在相同批准 base 新增报告文件服务并修复首 LF；提交后实际核验源码哈希与新内审读回一致，git 仅受保护 AGENTS 未暂存，未 push。随后只追加提交记录，不改受审源码。下一交付是消费实际批准的 checkpoint/凭据安全投影/原子导入接口并补真实 main picker 的正式接线，不把草案开放为迁移器；指定外审仍由总控预约。

本轮已通过只读 GitHub API 实查远端 develop 仍为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。不是仅依据根状态文件推断；当前没有可消费的格式基础 merge。上一 Goal 轮与本轮均有实质实现/验证进展，没有把静态状态或聊天意图记成 verified wait。

总控修正提示已全文读取，SHA `fc753a0fb54752ede1406689f3f7d5563f1f4bc391d0f1946d663c7bd60589a5`。完整包不强制原文件/推导/运行历史/会话；未选不得写入。无原文件仍可完整恢复当前状态，仅不可直接重跑；缺运行输入仅不承诺对应重放，不误降模板。

T09 获批只读输入版本 `873c8c051b9870aa12fc7e1dbbd3e0c358e7c380` 的 manifest 与 17 个固定文件已逐项哈希核验，记录在 evidence/approved-input-reference.json。仅核验固定输入，没有消费变化中 HEAD、未批准服务或用 expected 预填 Store；不增加产品通过数。

已在安全边界接收全文第九节及无桌面政策（共同指令 SHA `9717f699e14b5941e15d90269f33cbebc32ef9bec6e7439739be848753419880`），随后读取默认权限政策与 external-review-permissions.md。AGENTS 当前受保护 SHA `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759` 已实查；不暂存。权限只扩大两应用执行模式，不改变只读外审/模型/双审/付费/凭据或桌面边界；已透传独立内审 agent，未因此重跑产品检查。

本轮又全文读取共同指令 SHA `b24c4c88404f422c5fae4bf6c01e231b678e46741250801e8100cc62a31fec39`，仅同步已生效文件责任：T01 接管 storage 及格式 Python4/canonical7/main-engine1；T03 接管依赖/锁/构建四个文件；I06 保留其余六个 UI/bridge/main 文件，I05 其余未交文件。未消费任何未批实现，未扩大 T10 写权限；已透传内审 agent，不因此重测或重开 Goal/产品审查。旧指南记录保留。

## 依赖和完整验收

- T01/T00：批准的完整 checkpoint、原子只读导出和新项目原子发布导入，以及精确格式/角色 schema；当前 Store.state 不覆盖完整撤销与应用状态。
- T09/T08：真实逐 attempt 学习检查/提示/代做证据的受限投影；禁止由客户端自报独立掌握。
- T07：可支持的真实运行语义和重放输入验证。
- I06：vault、最小外发记录、端点凭据与发送授权始终排除，不能导出数据库整文件绕过选择项。
- 保留 FR-1000/1001/104、A-06–08、G.6、12.4/12.5、全部父功能和跨模块门。
- 尚未执行：正式接线、产品入口的真实 native picker、跨设备续编辑/查询/重跑冲突/撤销、真实学习联验、双平台包内与原生验证、指定双方新审、push/PR/CI/合并/发布。主进程新增触发的 e2e 要求保留；不在用户桌面启动旧 App e2e 冒充覆盖未接线服务。

本机只允许无窗口 CLI/unit/Python/build/unsigned 目录包，不启动 Electron/e2e/native/HMR，不读取凭据或外发业务数据；指定审查应用等待总控预约。

## 隔离 Linux 原生验证增量

在同一固定产品源码 `a8a497a8b1b7d52fcc365f8b128972867b2bd433` 上，新增独占路径测试工具完成真实 `showSaveDialog` 保存/取消；未改产品、共享测试/配置或启动 host GUI。独立审查推动修复隔离断言、命令硬超时、固定容器ID和镜像controls读回。attempt1启动前cap名称差异拦下，attempt2保存Enter无回执并超时；失败原件均保留。attempt3真实GTK截图、Alt+s保存/Escape取消、picker未改写、容器exit0，私有文件3896字节/0600/hash与服务回执及审查方独立生成预期逐字节一致。

容器实际非root1110、networknone/无挂载端口/defaultseccomp，额外SYS_ADMIN公开；renderer NoNewPrivs1/Seccomp2/CapEff0、sandbox/contextIsolation true、Node false。短时main loopback inspector在picker前关闭。此为Linux arm64私有服务native保存/取消，不提升为通用e2e、正式App/可信投影、G.6、跨平台或包内完成。详情：`isolated-native-review.md`、`../../iterations/T10/isolated-native-validation.md`、`evidence/isolated-native/manifest.json`（SHA256 `9e515ec939ff5ef732b88955da9b0360d08bae243abcecf7cf58cd6c512e31e1`）。

工具最终整仓check先遇既有engine-connection-state测试TIMEOUT（690通过/1失败），单文件8项复测通过，随后完整retry实际exit0，691TS/1112Python及lint/格式/类型/构建通过；失败和复测raw一并保留，未擅改共享测试，原因未证实。最后只读git ls-remote再次核验develop仍为5f910b52。私有阶段候选写在`private-stage-candidate.md`，待总控登记和指定外审租约；完整Goal保持未完成，未push/PR/CI/merge。

原生工具/原件冻结提交：`66eeedd735370576b49eb39cd4b14cdef9c0d55b`，manifest含55个原件，已再逐hash核验。随后按总控要求完成I06 §2–3回应提案，`../../iterations/T10/i06-trusted-transfer-contract-request.md`（SHA256 `6e52cdf4230b61034366963ef39808cbdf8b7e62655a0ec168d77706b311b7bd`）；2项合同歧义P2已修复并独立复核。该提案待owner批准，没有把guard、白名单或真实X1–X6写成已实现/已验；不因此修改产品、共享方法或既有测试。


总控已依据固定66eeedd独立读回登记待审T10-S1，未使双审/推送/正式格式或投影生效。原线按E1保全40个既有raw/browser/合成HTML（含11个历史summary逐hash原件）；旧browser3900B/26af与新native3896B/ad367是不同实物。另从已停同一attempt3容器补存三份cjs输出，明确仅为运行后读回；不改旧55项manifest或追称运行时独立输出归档。两条旧snapshot引用文件已不在，索引记录缺口。详见evidence-preservation-E1.md。没有重跑浏览器/产品或扩大包内证据。


已为登记阶段准备离线双外审完整任务正文和固定Git输入清单：external-review-task-packet.md、external-review-input-manifest.json。清单绑定a1e7efef候选的141个delta及6个不变上下文，已逐Git blob读回hash；66之后无产品/测试/依赖变动。该文件仅准备输入，尚无本线实际审查任务/模型终态/报告，不占用GUI或触发push；实际派发前仍须核验新基线、冻结树及总控资源租约。

## 当前 Goal 状态：blocked（未完成）

本轮已完成连续三轮同一依赖/资源条件的阻塞审计，见blocked-audit.md。正式格式/可信投影/位置lease/导入receipt仍无批准接点；外审实际任务0且无本线可用合规入口。私有实现、验证、内审、E1及离线packet已收口，现无不越界的必要独立实现可继续。总控/T01/I06实际进程仍运行，不把它们当停止；Goal blocked仅等待实际可执行接点或外审资源变化。完整目标与父门全部保留，候选和原件不变，未push/PR/CI/merge。


## 2026-10-22 实际双审启动

当前桌面政策已撤回静默/用户时段/CLI登录前置，旧限制仅为历史。总控给定短时创建lease后，已完成两隔离树准备与独立预检，准备提交`30ec443173d1f69925679d2f440516c49fa755f8`。原147项Git输入、产品C和证据A不改；两审查树detached77并拥有各自依赖、report/raw/scratch。

ZCode真实session `session_65271e095f85aad0c95b5e1f512243f1`、turn `turn_6b38be66-cb82-46f7-836a-43b742cfe944`，GLM-5.3/max/yolo；MiniMax真实session `mvs_41069a5454874e1aa0bd61c40d1daffa`、turn `854a6900-aadf-4f1e-b035-5806dc1cf2c8`，MiniMax-M3.1-Flash/xhigh、任务始终授权。两者实际cwd、完整290行输入和受理均已实核，已后台开始；前台已释放。完整回执见`dispatch-20261022/launch-receipt.json`与README。此前blocked审计中“实际任务0/无入口”为当时事实，现更新为实际任务2，尚无终态或指定Pass。

本次只推进已明确授权的准备和派发，没有重建/自动恢复或完成原blocked Goal；正式格式/可信投影/生产lease/导入receipt及父门仍待，未push/PR/CI/merge。准备方不重跑不变产品；审者允许在各自隔离env/scratch执行必要完整验证及独立反例，现有源/tests/fixture/锁/config/旧验收/旧raw/Git只读。


## 2026-10-22 round-1终态与修后候选

两指定任务现均实际终态stop，完整原报告、终态与验证raw已保全于round-1/。ZCode报告SHA6d46ea401d7ee6257766a162d79af6db2dd0e7cff448a8ac850a4297c6382f13；MiniMax报告SHAcb76b0a248575f348d6a8f24a30f8e4abf0fa788f78c7c4f30f17850ca5bd74f。两原报告均写有界阶段通过，但MiniMax登记EOCD计数P2，本线按较高优先级采纳修复，旧结论不继承到修后候选。10个去重议题的完整处置见round-1-disposition.md，包括已修、正式格式/共享owner与生命周期开放项；O4未修不得标关闭。

本轮仅改Python检查器/其测试、CLI probe输出目录与运行说明。定向66Python通过，整仓npm run check一次exit0，691TS/1118Python及lint/格式/类型/构建通过；独立补丁审查和20项内存反例通过。probe实际生成3HTML，3900B/26af字节保持不变且输出被忽略，旧证据不覆盖。新原件见round-2-preparation/verification.json。浏览器/native同一report源码不同标题输入、executed:null仅未观测哨兵的精确澄清见处置文档，旧原件不改。

新候选仍需双方各全新完整同版round-2审查，不复用旧会话；尚无新任务/创建lease，不操作GUI。原正式格式/可信投影/生产lease/原子导入及父门继续未完成，原Goal blocked不重建，未push/PR/CI/merge。

## 2026-10-22 round-2实际启动与完整正文受理

总控预检接受后给原T10短GUI创建lease，已各新建一个完整独立任务；前台创建/设置/输入读回完成即释放，不等待后台推理。固定reviewHead为66cc15200611d592d3da2877961f9e079eb05277，两审查树分别T10-zcode-review-r2-66cc152与T10-minimax-review-r2-66cc152。

ZCode真实session `session_51c6a1c550181572a24f331b9a5c5e23`、turn `turn_024c2267-49dd-4c90-9e0a-8dd9b61c5b43`，GLM-5.3/max、runtime yolo；MiniMax真实session `mvs_d314cc7a43c84a559e31d5ddf3663af7`、turn `5ad5f9d9-3db0-4872-86ab-04fbb3375fd3`，MiniMax-M3.1-Flash/xhigh、任务UI始终授权；各自实际cwd已核。Z106452B/a612c2e8、M106507B/a503367f完整附件byte-exact；Z自动Read1–551并由首工具补读552–667，M五read覆盖全部667行，逐行与冻结全文一致。真实回执及仅含本人提示编号行/调用标识的最小供给证据在round-2-dispatch/；完整上下文原件只在受限Git忽略目录保留，MiniMax初始链为12条消息，Z668仅空白格式尾行。

225项受审Git/工作文件与各11输入副本启动后保持精确；额外metadata仅路径/lstat及明确自身session归属，未知不读、不删求绿。未改其他会话/stdio/设置、未复用旧task/Pass、未互泄本轮意见。当前只记新任务启动/全文受理，正式终态/报告/问题闭环仍待；不因此标新候选或完整父T10通过，原Goal blocked不重建，未push/PR/CI/merge。
